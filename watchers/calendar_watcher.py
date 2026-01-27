"""
Calendar Watcher - Monitors Google Calendar for upcoming events

This watcher uses the Google Calendar API to check for upcoming
events and creates action files for events requiring preparation.

Setup:
1. Enable Calendar API in Google Cloud Console
2. Use the same OAuth credentials as Gmail (add calendar scope)
"""

import os
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .base_watcher import BaseWatcher
from .error_recovery import with_retry, ErrorCategory
from .deduplication import Deduplication


# Calendar API scopes (includes Gmail for shared auth)
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.readonly",
]


class CalendarWatcher(BaseWatcher):
    """
    Watches Google Calendar for upcoming events.

    Monitors for:
    - Events in the next 24 hours
    - Events requiring preparation
    - New meeting requests
    """

    # Keywords indicating preparation needed
    PREP_KEYWORDS = [
        "meeting", "call", "interview", "presentation",
        "demo", "review", "planning", "strategy",
    ]

    def __init__(
        self,
        vault_path: str,
        credentials_path: Optional[str] = None,
        token_path: Optional[str] = None,
        calendar_id: str = "primary",
        check_interval: int = 300,
        look_ahead_hours: int = 24,
        dry_run: bool = False,
    ):
        """
        Initialize the Calendar Watcher.

        Args:
            vault_path: Path to the Obsidian vault
            credentials_path: Path to OAuth credentials.json
            token_path: Path to save/load token.json
            calendar_id: Google Calendar ID (default: primary)
            check_interval: Seconds between checks (default: 300)
            look_ahead_hours: How many hours ahead to check (default: 24)
            dry_run: If True, don't create files
        """
        super().__init__(vault_path, check_interval, dry_run)
        self.credentials_path = credentials_path
        self.token_path = token_path or str(Path(vault_path) / ".calendar_token.json")
        self.calendar_id = calendar_id
        self.look_ahead_hours = look_ahead_hours
        self.service = None

        # Use persistent deduplication instead of in-memory set
        self.dedup = Deduplication(
            vault_path=vault_path,
            state_file=".calendar_state.json",
            item_prefix="CAL",
            scan_folders=True
        )

        self._authenticate()

    def _authenticate(self) -> None:
        """Authenticate with Calendar API using OAuth."""
        creds = None

        # Load existing token if available
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path or not os.path.exists(self.credentials_path):
                    raise ValueError(
                        "Credentials not found. Please provide credentials_path "
                        "with OAuth credentials.json."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(self.token_path, "w", encoding='utf-8') as token:
                token.write(creds.to_json())

        self.service = build("calendar", "v3", credentials=creds)
        self.logger.info("Calendar API authenticated successfully")

    @with_retry(max_attempts=3, base_delay=2, max_delay=60)
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for upcoming calendar events.

        Returns:
            List of event dictionaries
        """
        try:
            # Calculate time range (using timezone-aware datetime)
            now = datetime.now(timezone.utc)
            time_max = now + timedelta(hours=self.look_ahead_hours)

            # Fetch events
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=now.isoformat(),
                timeMax=time_max.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            ).execute()

            events = events_result.get("items", [])
            self.logger.info(f"Found {len(events)} upcoming events")

            # Filter out already processed events using persistent deduplication
            new_events = []
            for e in events:
                event_id = e.get("id")
                if not self.dedup.is_processed(event_id):
                    new_events.append(e)
                    # Mark as processed immediately to prevent duplicates
                    self.dedup.mark_processed(event_id)

            # Log to audit
            self._log_audit_action("calendar_check", {
                "events_found": len(new_events),
                "total_events": len(events),
                "look_ahead_hours": self.look_ahead_hours
            })

            return new_events

        except HttpError as e:
            self.logger.error(f"Calendar API error: {e}")
            return []

    def get_item_id(self, item: Dict[str, Any]) -> str:
        """Get unique ID for a calendar event."""
        return f"CAL_{item['id']}"

    def create_action_file(self, item: Dict[str, Any]) -> Optional[Path]:
        """
        Create a markdown action file for a calendar event.

        Args:
            item: Event dictionary from check_for_updates()

        Returns:
            Path to created file
        """
        event = item
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = self._sanitize_filename(event.get("summary", "No Title")[:50])
        filename = f"EVENT_{timestamp}_{safe_title}.md"
        filepath = self.needs_action / filename

        # Extract event details
        start = self._parse_event_time(event.get("start", {}))
        end = self._parse_event_time(event.get("end", {}))
        description = event.get("description", "No description")
        location = event.get("location", "No location specified")
        attendees = event.get("attendees", [])
        creator = event.get("creator", {}).get("email", "Unknown")

        # Determine if preparation is needed
        needs_prep = self._needs_preparation(event)

        # Calculate time until event
        time_until = self._time_until_str(start)

        priority = "!! MEDIUM"
        if needs_prep:
            priority = "!!! HIGH"
        elif time_until and "hour" in time_until and int(time_until.split()[0]) <= 2:
            priority = "!!! URGENT"

        content = f"""---
type: calendar_event
source: google_calendar
event_id: {event['id']}
calendar: {self.calendar_id}
title: {event.get('summary', 'No Title')}
start: {start}
end: {end}
location: {location}
creator: {creator}
needs_preparation: {needs_prep}
priority: {priority}
status: pending
created: {datetime.now().isoformat()}
---

# Event: {event.get('summary', 'No Title')}

**When:** {start} - {end}
**Where:** {location}
**Created by:** {creator}
**Time until:** {time_until or "TBD"}

## Attendees

{self._format_attendees(attendees)}

## Description

{description}

---

## Preparation Checklist

{"- [ ] Review meeting agenda" if needs_prep else ""}
- [ ] Check if any pre-work required
- [ ] Prepare relevant documents/notes
- [ ] Review attendee list
- [ ] Plan talking points

## Questions to Consider

- What is the goal of this meeting?
- What decisions need to be made?
- Do I need to prepare anything to share?

## After Meeting

- [ ] Send follow-up email if needed
- [ ] Move to Done folder
- [ ] Note any action items

"""

        filepath.write_text(content, encoding="utf-8")
        self.logger.info(f"Created action file: {filepath.name}")

        # Log to audit
        self._log_audit_action("calendar_action_file_created", {
            "event_id": event.get("id"),
            "title": event.get("summary", "No Title"),
            "start": start,
            "location": location,
            "needs_prep": needs_prep,
            "filepath": str(filepath)
        })

        return filepath

    def _parse_event_time(self, time_data: Dict[str, str]) -> str:
        """Parse event start/end time to readable string."""
        if "dateTime" in time_data:
            # Parse RFC3339 format
            try:
                dt = datetime.fromisoformat(
                    time_data["dateTime"].replace("Z", "+00:00")
                )
                return dt.strftime("%Y-%m-%d %H:%M")
            except:
                return time_data.get("dateTime", "Unknown")
        else:
            # All-day event
            return time_data.get("date", "Unknown")

    def _needs_preparation(self, event: Dict[str, Any]) -> bool:
        """Check if event requires preparation."""
        title = event.get("summary", "").lower()
        description = event.get("description", "").lower()

        text = f"{title} {description}"

        for keyword in self.PREP_KEYWORDS:
            if keyword in text:
                return True

        return False

    def _time_until_str(self, event_time: str) -> Optional[str]:
        """Calculate time until event as human-readable string."""
        try:
            # Try to parse the time string
            event_dt = None
            for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    event_dt = datetime.strptime(event_time, fmt)
                    # Assume parsed time is in local timezone, make it aware
                    event_dt = event_dt.replace(tzinfo=timezone.utc)
                    break
                except ValueError:
                    continue

            if not event_dt:
                return None

            # Use UTC now for consistent comparison (both are timezone-aware)
            now = datetime.now(timezone.utc)
            delta = event_dt - now

            if delta.total_seconds() <= 0:
                return "Now/Passed"

            hours = int(delta.total_seconds() // 3600)
            minutes = int((delta.total_seconds() % 3600) // 60)

            if hours > 24:
                days = hours // 24
                return f"{days} day{'s' if days > 1 else ''}"
            elif hours > 0:
                return f"{hours} hour{'s' if hours > 1 else ''} {minutes} min"
            else:
                return f"{minutes} minute{'s' if minutes > 1 else ''}"

        except Exception:
            return None

    def _format_attendees(self, attendees: List[Dict[str, Any]]) -> str:
        """Format attendee list for markdown."""
        if not attendees:
            return "No other attendees"

        lines = []
        for attendee in attendees[:10]:  # Limit to 10
            email = attendee.get("email", "Unknown")
            name = attendee.get("displayName", "")
            response = attendee.get("responseStatus", "needsAction")

            status_map = {
                "accepted": "✓",
                "declined": "✗",
                "tentative": "?",
                "needsAction": "○",
            }

            status = status_map.get(response, "○")
            lines.append(f"- {status} {name} ({email})" if name else f"- {status} {email}")

        if len(attendees) > 10:
            lines.append(f"- ... and {len(attendees) - 10} more")

        return "\n".join(lines) if lines else "No other attendees"

    def _sanitize_filename(self, name: str) -> str:
        """Remove characters not safe for filenames."""
        unsafe = '<>:"/\\|?*'
        for char in unsafe:
            name = name.replace(char, "_")
        name = name.strip(". ")
        return name or "no_title"

    def _log_audit_action(self, action_type: str, parameters: Dict[str, Any], result: str = "success"):
        """
        Log action to audit log.

        Args:
            action_type: Type of action performed
            parameters: Action parameters
            result: Result of action (success/error)
        """
        try:
            from utils.audit_logging import AuditLogger

            audit_logger = AuditLogger(self.vault_path)
            audit_logger.log_action(
                action_type=action_type,
                target="calendar",
                parameters=parameters,
                result=result
            )
        except Exception as e:
            self.logger.debug(f"Could not log to audit log: {e}")


def main():
    """Entry point for running the Calendar watcher directly."""
    import argparse

    parser = argparse.ArgumentParser(description="Calendar Watcher for Personal AI Employee")
    parser.add_argument(
        "--vault",
        default=".",
        help="Path to Obsidian vault (default: current directory)"
    )
    parser.add_argument(
        "--credentials",
        help="Path to OAuth credentials.json"
    )
    parser.add_argument(
        "--token",
        help="Path to save/load token.json"
    )
    parser.add_argument(
        "--calendar-id",
        default="primary",
        help="Google Calendar ID (default: primary)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Check interval in seconds (default: 300)"
    )
    parser.add_argument(
        "--look-ahead",
        type=int,
        default=24,
        help="Hours to look ahead for events (default: 24)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log actions without creating files"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit"
    )

    args = parser.parse_args()

    watcher = CalendarWatcher(
        vault_path=args.vault,
        credentials_path=args.credentials,
        token_path=args.token,
        calendar_id=args.calendar_id,
        check_interval=args.interval,
        look_ahead_hours=args.look_ahead,
        dry_run=args.dry_run,
    )

    if args.once:
        items = watcher.run_once()
        print(f"Found {len(items)} upcoming events")
        for item in items:
            print(f"  - {item.get('summary', 'No Title')}: {item.get('start', {})}")
    else:
        watcher.run()


if __name__ == "__main__":
    main()
