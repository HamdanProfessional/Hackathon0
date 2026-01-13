"""
Gmail Watcher - Monitors Gmail for new important messages

This watcher uses the Gmail API to check for unread/important emails
and creates action files in the vault for items needing attention.

Setup:
1. Enable Gmail API in Google Cloud Console
2. Create OAuth 2.0 credentials
3. Save credentials to token.json (run authenticate() first)
"""

import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .base_watcher import BaseWatcher
from .error_recovery import with_retry, ErrorCategory


# Gmail API scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailWatcher(BaseWatcher):
    """
    Watches Gmail for new unread/important messages.

    Monitors for:
    - Unread messages in inbox
    - Messages marked as important
    - Messages with urgent keywords
    """

    # Keywords that flag a message as urgent
    URGENT_KEYWORDS = [
        "urgent", "asap", "emergency", "immediately",
        "deadline", "due today", "due tomorrow",
        "invoice", "payment", "contract",
        "meeting", "call", "appointment",
        "cancel", "refund", "complaint",
    ]

    def __init__(
        self,
        vault_path: str,
        credentials_path: Optional[str] = None,
        token_path: Optional[str] = None,
        check_interval: int = 120,
        dry_run: bool = False,
    ):
        """
        Initialize the Gmail Watcher.

        Args:
            vault_path: Path to the Obsidian vault
            credentials_path: Path to OAuth credentials.json
            token_path: Path to save/load token.json
            check_interval: Seconds between checks (default: 120)
            dry_run: If True, don't create files
        """
        super().__init__(vault_path, check_interval, dry_run)
        self.credentials_path = credentials_path
        self.token_path = token_path or str(Path(vault_path) / ".gmail_token.json")
        self.service = None
        self._authenticate()

    def _authenticate(self) -> None:
        """Authenticate with Gmail API using OAuth."""
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
                        "with OAuth credentials.json, or run authenticate() first."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(self.token_path, "w") as token:
                token.write(creds.to_json())

        self.service = build("gmail", "v1", credentials=creds)
        self.logger.info("Gmail API authenticated successfully")

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new unread/important emails.

        Returns:
            List of message dictionaries with id, threadId, and basic info
        """
        try:
            # Search for unread important messages
            results = self.service.users().messages().list(
                userId="me",
                q="is:unread is:important OR is:unread",
                maxResults=20
            ).execute()

            messages = results.get("messages", [])
            self.logger.info(f"Found {len(messages)} unread messages")

            # Fetch full details for each message
            full_messages = []
            for msg in messages[:10]:  # Limit to 10 per check
                try:
                    full_msg = self._get_message_details(msg["id"])
                    if full_msg:
                        full_messages.append(full_msg)
                except HttpError as e:
                    self.logger.error(f"Error fetching message {msg['id']}: {e}")

            # Log to audit
            self._log_audit_action("gmail_check", {
                "messages_found": len(full_messages),
                "total_unread": len(messages)
            })

            return full_messages

        except HttpError as e:
            self.logger.error(f"Gmail API error: {e}")
            return []

    def _get_message_details(self, msg_id: str) -> Optional[Dict[str, Any]]:
        """Fetch full message details including headers and snippet."""
        try:
            msg = self.service.users().messages().get(
                userId="me",
                id=msg_id,
                format="metadata",
                metadataHeaders=["From", "To", "Subject", "Date"]
            ).execute()

            # Extract headers
            headers = {}
            for h in msg.get("payload", {}).get("headers", []):
                headers[h["name"]] = h["value"]

            # Determine urgency
            snippet = msg.get("snippet", "")
            subject = headers.get("Subject", "")
            urgency = self._assess_urgency(subject, snippet)

            return {
                "id": msg["id"],
                "threadId": msg.get("threadId", ""),
                "from": headers.get("From", "Unknown"),
                "to": headers.get("To", ""),
                "subject": headers.get("Subject", "No Subject"),
                "date": headers.get("Date", ""),
                "snippet": snippet,
                "urgency": urgency,
            }

        except HttpError as e:
            self.logger.error(f"Error fetching message details: {e}")
            return None

    def _assess_urgency(self, subject: str, snippet: str) -> str:
        """Assess message urgency based on keywords."""
        text = f"{subject} {snippet}".lower()

        for keyword in self.URGENT_KEYWORDS:
            if keyword in text:
                return "high"

        return "normal"

    def get_item_id(self, item: Dict[str, Any]) -> str:
        """Get unique ID for an email message."""
        return f"GMAIL_{item['id']}"

    def create_action_file(self, item: Dict[str, Any]) -> Optional[Path]:
        """
        Create a markdown action file for an email.

        Args:
            item: Message dictionary from check_for_updates()

        Returns:
            Path to created file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_subject = self._sanitize_filename(item["subject"][:50])
        filename = f"EMAIL_{timestamp}_{safe_subject}.md"
        filepath = self.needs_action / filename

        # Get priority based on urgency
        priority = "!!! HIGH" if item["urgency"] == "high" else "normal"

        content = f"""---
type: email
source: gmail
message_id: {item['id']}
thread_id: {item['threadId']}
from: {item['from']}
subject: {item['subject']}
received: {item['date']}
urgency: {item['urgency']}
priority: {priority}
status: pending
created: {datetime.now().isoformat()}
---

# Email: {item['subject']}

**From:** {item['from']}
**Date:** {item['date']}
**Urgency:** {item['urgency']}

## Preview

{item['snippet']}

---

## Suggested Actions

- [ ] Read full email content
- [ ] Categorize: Action Required / Information Only / Delegate / Archive
- [ ] Draft response if needed
- [ ] Move to Done when complete

## Notes

<!-- Add your notes here -->

"""

        filepath.write_text(content, encoding="utf-8")
        self.logger.info(f"Created action file: {filepath.name}")

        # Log to audit
        self._log_audit_action("email_action_file_created", {
            "message_id": item['id'],
            "subject": item['subject'],
            "from": item['from'],
            "urgency": item['urgency'],
            "filepath": str(filepath)
        })

        return filepath

    def _sanitize_filename(self, name: str) -> str:
        """Remove characters not safe for filenames."""
        # Replace unsafe characters with underscore
        unsafe = '<>:"/\\|?*'
        for char in unsafe:
            name = name.replace(char, "_")
        # Also remove leading/trailing spaces and dots
        name = name.strip(". ")
        return name or "no_subject"

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
                target="gmail",
                parameters=parameters,
                result=result
            )
        except Exception as e:
            self.logger.debug(f"Could not log to audit log: {e}")

    @staticmethod
    def authenticate(credentials_path: str, token_path: str) -> None:
        """
        Run the OAuth flow to authenticate with Gmail.

        Call this once to set up credentials before running the watcher.

        Args:
            credentials_path: Path to OAuth credentials.json
            token_path: Where to save the access token
        """
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path, SCOPES
        )
        creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token:
            token.write(creds.to_json())

        print(f"Authentication successful! Token saved to {token_path}")


def main():
    """Entry point for running the Gmail watcher directly."""
    import argparse

    parser = argparse.ArgumentParser(description="Gmail Watcher for Personal AI Employee")
    parser.add_argument(
        "--vault",
        default=".",
        help="Path to Obsidian vault (default: current directory)"
    )
    parser.add_argument(
        "--credentials",
        help="Path to Gmail OAuth credentials.json"
    )
    parser.add_argument(
        "--token",
        help="Path to save/load token.json"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=120,
        help="Check interval in seconds (default: 120)"
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

    watcher = GmailWatcher(
        vault_path=args.vault,
        credentials_path=args.credentials,
        token_path=args.token,
        check_interval=args.interval,
        dry_run=args.dry_run,
    )

    if args.once:
        items = watcher.run_once()
        print(f"Found {len(items)} new items")
        for item in items:
            print(f"  - {item['subject']}")
    else:
        watcher.run()


if __name__ == "__main__":
    main()
