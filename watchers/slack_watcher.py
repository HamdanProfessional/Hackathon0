"""
Slack Watcher - Monitors Slack for important messages

This watcher uses the Slack API to check for new messages in channels
and DMs, creating action files in the vault for items needing attention.

Setup:
1. Create a Slack App at https://api.slack.com/apps
2. Enable OAuth scopes: channels:history, groups:history, im:history, mpim:history
3. Install the app and get the Bot Token
4. Set SLACK_BOT_TOKEN environment variable
"""

import os
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
except ImportError:
    raise ImportError("slack-sdk is required. Install with: pip install slack-sdk")

from .base_watcher import BaseWatcher
from .error_recovery import with_retry, ErrorCategory


class SlackWatcher(BaseWatcher):
    """
    Watches Slack for new important messages.

    Monitors for:
    - Mentions of the bot/user
    - DMs
    - Messages with urgent keywords
    - Messages in specific channels
    """

    # Keywords that flag a message as urgent
    URGENT_KEYWORDS = [
        "urgent", "asap", "emergency", "immediately",
        "deadline", "due today", "due tomorrow",
        "invoice", "payment", "contract",
        "meeting", "call", "appointment",
        "cancel", "refund", "complaint",
        "bug", "critical", "production",
        "server down", "error", "exception",
    ]

    def __init__(
        self,
        vault_path: str,
        bot_token: Optional[str] = None,
        user_id: Optional[str] = None,
        channels_to_watch: Optional[List[str]] = None,
        check_interval: int = 60,
        dry_run: bool = False,
    ):
        """
        Initialize the Slack Watcher.

        Args:
            vault_path: Path to the Obsidian vault
            bot_token: Slack Bot Token (xoxb-...)
            user_id: Your Slack User ID to detect mentions
            channels_to_watch: List of channel IDs to monitor
            check_interval: Seconds between checks (default: 60)
            dry_run: If True, don't create files
        """
        super().__init__(vault_path, check_interval, dry_run)

        self.bot_token = bot_token or os.getenv("SLACK_BOT_TOKEN")
        if not self.bot_token:
            raise ValueError("SLACK_BOT_TOKEN environment variable must be set")

        self.user_id = user_id or os.getenv("SLACK_USER_ID")
        self.channels_to_watch = channels_to_watch or []

        self.client = WebClient(token=self.bot_token)
        self.processed_ids = set()
        self.last_check_time = datetime.utcnow() - timedelta(minutes=5)

        # Get bot user info
        try:
            auth_info = self.client.auth_test()
            self.bot_user_id = auth_info["user_id"]
            self.logger.info(f"Authenticated as bot user: {auth_info['user']}")
        except SlackApiError as e:
            self.logger.error(f"Failed to authenticate with Slack: {e}")
            raise

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new Slack messages.

        Returns:
            List of new messages needing attention
        """
        new_messages = []

        try:
            # Get all conversations (channels, DMs, MPIMs)
            conversations = self._get_conversations()

            for conversation in conversations:
                channel_id = conversation["id"]
                channel_name = conversation.get("name", "DM")

                # Skip if not in watch list (if list is specified)
                if self.channels_to_watch and channel_id not in self.channels_to_watch:
                    continue

                # Get messages since last check
                messages = self._get_messages(channel_id)

                for msg in messages:
                    # Skip messages that are too old
                    msg_time = datetime.fromtimestamp(float(msg["ts"]))
                    if msg_time < self.last_check_time:
                        continue

                    # Skip already processed
                    if msg["ts"] in self.processed_ids:
                        continue

                    # Check if message needs attention
                    if self._needs_attention(msg):
                        new_messages.append({
                            "message": msg,
                            "channel_id": channel_id,
                            "channel_name": channel_name,
                            "timestamp": msg_time,
                        })
                        self.processed_ids.add(msg["ts"])

        except SlackApiError as e:
            self.logger.error(f"Slack API error: {e}")

        self.last_check_time = datetime.utcnow()

        # Log to audit
        self._log_audit_action("slack_check", {
            "messages_found": len(new_messages),
            "conversations_checked": len(conversations) if 'conversations' in locals() else 0
        })

        return new_messages

    def _get_conversations(self) -> List[Dict[str, Any]]:
        """Get all conversations the bot has access to."""
        conversations = []
        cursor = None

        try:
            # Get public channels
            while True:
                response = self.client.conversations_list(
                    types="public_channel,private_channel,mpim,im",
                    cursor=cursor,
                    limit=100
                )

                # Validate response has channels field before accessing
                channels = response.get("channels")
                if channels is not None:
                    conversations.extend(channels)
                else:
                    self.logger.warning(f"Response missing 'channels' field: {response}")
                    break

                cursor = response.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break

        except SlackApiError as e:
            self.logger.error(f"Error getting conversations: {e}")

        return conversations

    def _get_messages(self, channel_id: str) -> List[Dict[str, Any]]:
        """Get messages from a channel since last check."""
        messages = []

        try:
            # Get conversation history
            response = self.client.conversations_history(
                channel=channel_id,
                oldest=str(self.last_check_time.timestamp()),
                limit=50
            )

            messages = response.get("messages", [])

        except SlackApiError as e:
            if e.response["error"] != "not_in_channel":
                self.logger.error(f"Error getting messages from {channel_id}: {e}")

        return messages

    def _needs_attention(self, message: Dict[str, Any]) -> bool:
        """
        Check if a message needs attention.

        A message needs attention if:
        - It's a DM
        - It mentions the bot or user
        - It contains urgent keywords
        """
        text = message.get("text", "").lower()

        # Check for DM (IM channel)
        if message.get("channel", "").startswith("D"):
            return True

        # Check for mentions
        if f"<@{self.bot_user_id}>" in message.get("text", ""):
            return True

        if self.user_id and f"<@{self.user_id}>" in message.get("text", ""):
            return True

        # Check for urgent keywords
        for keyword in self.URGENT_KEYWORDS:
            if keyword.lower() in text:
                return True

        return False

    def create_action_file(self, item: Dict[str, Any]) -> Optional[Path]:
        """
        Create a markdown action file for the Slack message.

        Args:
            item: Message item from check_for_updates()

        Returns:
            Path to the created file
        """
        msg = item["message"]
        channel_name = item["channel_name"]
        timestamp = item["timestamp"]

        # Get sender info
        user_id = msg.get("user", "Unknown")
        sender = self._get_user_name(user_id)

        # Format content
        content = f"""---
type: slack_message
service: slack
channel: {channel_name}
sender: {sender}
timestamp: {timestamp.isoformat()}
message_id: {msg['ts']}
priority: {"high" if any(kw in msg.get("text", "").lower() for kw in self.URGENT_KEYWORDS) else "medium"}
status: pending
---

# Slack Message from {sender}

**Channel:** #{channel_name}
**Time:** {timestamp.strftime("%Y-%m-%d %H:%M:%S")}

## Message

{msg.get('text', 'No text')}

## Suggested Actions

- [ ] Reply to the message
- [ ] Create a task if needed
- [ ] Archive after processing

## Context

- **Sender:** {sender} ({user_id})
- **Message Link:** https://slack.com/archives/{item['channel_id']}/p{msg['ts'].replace('.', '')}

---
*Generated by AI Employee Slack Watcher*
"""

        # Create filename
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"SLACK_{timestamp_str}_{channel_name}.md"

        filepath = self.needs_action / filename

        if not self.dry_run:
            filepath.write_text(content)
            self.logger.info(f"Created action file: {filepath}")
        else:
            self.logger.info(f"[DRY RUN] Would create: {filepath}")

        # Log to audit
        self._log_audit_action("slack_action_file_created", {
            "channel": channel_name,
            "sender": sender,
            "timestamp": timestamp.isoformat(),
            "filepath": str(filepath),
            "message_id": msg['ts']
        })

        return filepath

    def get_item_id(self, item: Dict[str, Any]) -> str:
        """Get unique ID for a message (timestamp)."""
        return item["message"]["ts"]

    def _get_user_name(self, user_id: str) -> str:
        """Get user's display name from user ID."""
        try:
            response = self.client.users_info(user=user_id)
            return response["user"]["real_name"] or response["user"]["name"]
        except SlackApiError:
            return user_id

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
                target="slack",
                parameters=parameters,
                result=result
            )
        except Exception as e:
            self.logger.debug(f"Could not log to audit log: {e}")


def main():
    """Run the Slack watcher."""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor Slack for important messages")
    parser.add_argument("--vault", default="AI_Employee_Vault", help="Path to vault")
    parser.add_argument("--token", help="Slack Bot Token (or set SLACK_BOT_TOKEN env var)")
    parser.add_argument("--user-id", help="Your Slack User ID (or set SLACK_USER_ID env var)")
    parser.add_argument("--channels", nargs="+", help="Channel IDs to watch")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--dry-run", action="store_true", help="Log but don't create files")

    args = parser.parse_args()

    watcher = SlackWatcher(
        vault_path=args.vault,
        bot_token=args.token,
        user_id=args.user_id,
        channels_to_watch=args.channels,
        check_interval=args.interval,
        dry_run=args.dry_run,
    )

    if args.once:
        items = watcher.check_for_updates()
        for item in items:
            watcher.create_action_file(item)
        print(f"Found {len(items)} new messages")
    else:
        watcher.run()


if __name__ == "__main__":
    main()
