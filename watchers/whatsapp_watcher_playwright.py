#!/usr/bin/env python3
"""
WhatsApp Watcher (Playwright-based)

Monitors WhatsApp Web for important messages using Playwright.
This is the official approach shown in Hackathon0.md.

Usage:
    python whatsapp_watcher_playwright.py --vault . --session ./whatsapp_session
    python whatsapp_watcher_playwright.py --vault . --session ./whatsapp_session --once
"""

import sys
import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Error: Playwright not installed.")
    print("Please run:")
    print("  pip install playwright")
    print("  playwright install chromium")
    sys.exit(1)

from watchers.base_watcher import BaseWatcher
from .error_recovery import with_retry, ErrorCategory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class WhatsAppWatcherPlaywright(BaseWatcher):
    """
    Monitor WhatsApp Web for important messages using Playwright.

    This uses the approach from Hackathon0.md:
    - Launch persistent browser session (stays logged in)
    - Monitor WhatsApp Web
    - Extract unread messages with keywords
    - Create action files
    """

    # Keywords that trigger action
    KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'watch']

    def __init__(self, vault_path: str, session_path: str, check_interval: int = 30, headless: bool = False):
        """
        Initialize WhatsApp watcher.

        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to store browser session (stays logged in)
            check_interval: Seconds between checks (default: 30)
            headless: Run headless mode (default: False for first-time setup)
        """
        super().__init__(vault_path, check_interval)

        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)

        self.headless = headless
        self.processed_messages = set()

        logger.info(f"WhatsApp watcher initialized with Playwright")
        logger.info(f"Session path: {self.session_path}")
        logger.info(f"Headless: {headless}")

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new unread WhatsApp messages.

        Returns:
            List of message dictionaries
        """
        messages = []

        try:
            with sync_playwright() as p:
                # Launch with persistent session
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=self.headless,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled'
                    ]
                )

                # Create page (or get existing)
                if len(browser.pages) == 0:
                    page = browser.new_page()
                else:
                    page = browser.pages[0]

                # Navigate to WhatsApp Web
                page.goto('https://web.whatsapp.com', timeout=60000)

                # Wait for page to load and check if logged in
                logger.info("Waiting for WhatsApp Web to load...")

                # Wait for page to be ready
                time.sleep(5)

                # Check multiple indicators of login status
                logged_in = False
                for attempt in range(5):  # Try 5 times with 5 second intervals
                    try:
                        # Multiple possible selectors for logged-in state
                        chat_selectors = [
                            '[data-testid="chat-list"]',
                            '#side > div',
                            'div[role="application"]',
                            '#pane-side'
                        ]

                        # QR code selectors
                        qr_selectors = [
                            'canvas[aria-label*="QR"]',
                            'canvas[aria-label*="Scan"]',
                            '[data-testid="qrcode"]',
                            'div[data-refid="qrcode"]'
                        ]

                        # Check if logged in (any chat selector exists)
                        for selector in chat_selectors:
                            if page.query_selector(selector):
                                logger.info(f"✅ Detected logged in (found: {selector})!")
                                logged_in = True
                                break

                        if logged_in:
                            break

                        # Check if QR code is showing
                        for selector in qr_selectors:
                            if page.query_selector(selector):
                                logger.warning(f"⚠️  QR code detected (attempt {attempt + 1}/5). Waiting 5 seconds...")
                                time.sleep(5)
                                break
                        else:
                            # Page still loading or unknown state
                            logger.info(f"Checking login status... (attempt {attempt + 1}/5)")
                            time.sleep(5)

                    except Exception as e:
                        logger.debug(f"Check attempt {attempt + 1} failed: {e}")
                        time.sleep(5)

                if logged_in:
                    # Get unread messages
                    logger.info("Proceeding to check for unread messages...")
                    messages = self._get_unread_messages(page)
                else:
                    logger.warning("❌ Could not confirm login after 5 attempts")
                    # Try to proceed anyway and check for messages
                    logger.info("Attempting to check for messages anyway...")
                    messages = self._get_unread_messages(page)

                browser.close()

        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            # Log audit action for failed check
            self._log_audit_action("whatsapp_check", {
                "status": "failed",
                "error": str(e)
            }, result="failed")
            return messages

        # Log audit action for successful check
        self._log_audit_action("whatsapp_check", {
            "messages_found": len(messages),
            "keywords_checked": ", ".join(self.KEYWORDS)
        })

        return messages

    def _get_unread_messages(self, page) -> List[Dict]:
        """
        Get all messages with keywords from recent chats.

        Note: Opening WhatsApp Web marks messages as read, so we scan
        recent chats instead of just unread ones.

        Args:
            page: Playwright page object

        Returns:
            List of message dictionaries
        """
        messages = []

        try:
            # Get all chat list items (not just unread)
            logger.info("Scanning recent chats for keywords...")

            # Use JavaScript to get clickable chat elements more reliably
            chat_info = page.evaluate("""() => {
                // Find top-level chat list items (not nested children)
                const side = document.querySelector('#side');
                if (!side) return {count: 0, selector: 'no-side'};

                // Look for the chat list container
                const chatList = side.querySelector('[data-testid="chat-list"]');
                if (!chatList) return {count: 0, selector: 'no-chat-list'};

                // Get DIRECT children of chat-list (not nested elements)
                const chatItems = Array.from(chatList.children).filter(el => {
                    const text = el.innerText || '';
                    const lines = text.split('\\n').filter(l => l.trim().length > 0);

                    // Must have at least 2 lines (name + message)
                    if (lines.length < 2) return false;

                    // Exclude system messages
                    const firstLine = lines[0].toLowerCase();
                    if (firstLine.includes('whatsapp') || firstLine.includes('get') ||
                        firstLine.includes('download') || firstLine.includes('search')) {
                        return false;
                    }

                    // Must be clickable
                    return el.getAttribute('role') === 'listitem' ||
                           el.getAttribute('tabindex') === '0' ||
                           el.onclick !== null;
                });

                if (chatItems.length > 0) {
                    return {
                        count: chatItems.length,
                        selector: 'chat-list-children',
                        total: chatList.children.length
                    };
                }

                return {count: 0, selector: 'no-items', total: chatList.children.length};
            }""")

            logger.info(f"Chat detection: {chat_info}")
            chat_count = chat_info.get('count', 0)

            logger.info(f"Found {chat_count} chat elements via JavaScript")

            if chat_count == 0:
                logger.warning("Could not find any chats")
                return messages

            # Limit to first 10 recent chats
            chats_to_check = min(10, chat_count)
            logger.info(f"Checking last {chats_to_check} chats for keywords: {', '.join(self.KEYWORDS)}")

            processed_ids = set()  # Avoid duplicates

            for i in range(chats_to_check):
                try:
                    logger.info(f"--- Processing chat {i} ---")

                    # Use JavaScript to click on the actual chat
                    clicked = page.evaluate(f"""(index) => {{
                        const side = document.querySelector('#side');
                        if (!side) return false;

                        const chatList = side.querySelector('[data-testid="chat-list"]');
                        if (!chatList) return false;

                        // Get DIRECT children (not nested elements)
                        const chatItems = Array.from(chatList.children).filter(el => {{
                            const text = el.innerText || '';
                            const lines = text.split('\\n').filter(l => l.trim().length > 0);

                            if (lines.length < 2) return false;

                            const firstLine = lines[0].toLowerCase();
                            if (firstLine.includes('whatsapp') || firstLine.includes('get') ||
                                firstLine.includes('download') || firstLine.includes('search')) {{
                                return false;
                            }}

                            return el.getAttribute('role') === 'listitem' ||
                                   el.getAttribute('tabindex') === '0' ||
                                   el.onclick !== null;
                        }});

                        if (chatItems.length > 0 && index < chatItems.length) {{
                            chatItems[index].scrollIntoView();
                            chatItems[index].click();
                            return true;
                        }}

                        return false;
                    }}""", i)

                    if not clicked:
                        logger.warning(f"Could not click chat {i}")
                        continue

                    logger.info(f"Clicked chat {i}, waiting for load...")
                    time.sleep(1.0)  # Wait for chat to load

                    # Get sender name first
                    sender = self._get_sender_name(page)
                    logger.info(f"Sender: {sender}")

                    # Get messages from this chat
                    chat_messages = page.query_selector_all('[data-testid="msg-container"]')

                    # DEBUG: Check if we're actually in a chat
                    chat_content = page.evaluate("""() => {
                        const main = document.querySelector('#main');
                        if (!main) return 'No main element';

                        const messages = main.querySelectorAll('[data-testid="msg-container"], [data-testid="msg"]');
                        return {
                            mainExists: true,
                            msgContainers: messages.length,
                            innerText: main.innerText.substring(0, 200)
                        };
                    }""")
                    logger.info(f"DEBUG - Chat content: {chat_content}")
                    logger.info(f"Found {len(chat_messages)} messages with [data-testid='msg-container']")

                    # Check last 3 messages
                    for msg_idx, msg in enumerate(chat_messages[-3:]):
                        try:
                            msg_text = msg.inner_text()

                            # DEBUG: Log what we're seeing
                            logger.info(f"Chat {i} - Message {msg_idx} from {sender}: {msg_text[:100]}...")

                            if self._is_important(msg_text):
                                # Create unique ID based on sender and content
                                msg_id = f"WHATSAPP_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"

                                if msg_id not in processed_ids:
                                    processed_ids.add(msg_id)

                                    messages.append({
                                        'id': msg_id,
                                        'sender': sender,
                                        'content': msg_text,
                                        'timestamp': datetime.now().isoformat(),
                                        'index': i
                                    })

                                    logger.info(f"✓✓✓ FOUND KEYWORD in message from {sender}!")

                        except Exception as e:
                            logger.debug(f"Error extracting message: {e}")
                            continue

                    # Go back to chat list using JavaScript
                    logger.info(f"Going back to chat list...")
                    page.evaluate("""() => {
                        const backButton = document.querySelector('[data-icon="back"]') ||
                                          document.querySelector('div[role="button"][aria-label*="back"]');
                        if (backButton) backButton.click();
                    }""")
                    time.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error processing chat {i}: {e}")
                    # Try to go back if stuck
                    try:
                        page.evaluate("""() => {
                            const backButton = document.querySelector('[data-icon="back"]') ||
                                              document.querySelector('div[role="button"][aria-label*="back"]');
                            if (backButton) backButton.click();
                        }""")
                    except:
                        pass
                    continue

        except Exception as e:
            logger.error(f"Error getting messages: {e}")

        return messages

    def _extract_message_content(self, page) -> Optional[str]:
        """
        Extract message text from the current chat.

        Args:
            page: Playwright page object

        Returns:
            Message text or None
        """
        try:
            # Wait for messages to load
            page.wait_for_selector('[data-testid="msg-container"]', timeout=5000)

            # Get the latest message (first visible)
            messages = page.query_selector_all('[data-testid="msg-container"]')

            if not messages:
                return None

            # Get the last message (most recent)
            latest_message = messages[-1]

            # Extract text content
            message_text = latest_message.inner_text()

            # Clean up
            message_text = ' '.join(message_text.split())

            return message_text if len(message_text) > 0 else None

        except Exception as e:
            logger.error(f"Error extracting message content: {e}")
            return None

    def _get_sender_name(self, page) -> str:
        """
        Get the sender/contact name from the current chat.

        Args:
            page: Playwright page object

        Returns:
            Sender name
        """
        try:
            # Use JavaScript to get contact name more reliably
            name = page.evaluate("""() => {
                // Try multiple selectors for contact name
                const selectors = [
                    '[data-testid="chat-title"]',
                    '[data-testid="conversation-title"]',
                    'span[title]',
                    '#main > header > div > div > span'
                ];

                for (const selector of selectors) {
                    const el = document.querySelector(selector);
                    if (el && el.innerText && el.innerText.trim()) {
                        const name = el.innerText.trim();
                        // Filter out page title like "(1) WhatsApp"
                        if (!name.includes('WhatsApp') || name.split('\\n').length > 1) {
                            return name;
                        }
                    }
                }

                // Last resort: get from first line of any header element
                const header = document.querySelector('#main header');
                if (header) {
                    const text = header.innerText || '';
                    const lines = text.split('\\n').filter(l => l.trim());
                    if (lines.length > 0 && !lines[0].includes('WhatsApp')) {
                        return lines[0];
                    }
                }

                return 'Unknown';
            }""")

            return name if name and name != "Unknown" else "Unknown"

        except Exception as e:
            logger.debug(f"Error getting sender name: {e}")
            return "Unknown"

    def _is_important(self, text: str) -> bool:
        """
        Check if message contains important keywords.

        Args:
            text: Message text

        Returns:
            True if message is important
        """
        text_lower = text.lower()

        for keyword in self.KEYWORDS:
            if keyword in text_lower:
                return True

        return False

    def get_item_id(self, item: Dict) -> str:
        """Get unique ID for a message."""
        return item.get('id', f"whatsapp_{int(time.time())}")

    def create_action_file(self, item: Dict) -> Optional[Path]:
        """
        Create action file in Needs_Action folder.

        Args:
            item: Message dictionary

        Returns:
            Path to created file
        """
        try:
            filename = f"WHATSAPP_{item['id']}.md"
            filepath = self.needs_action / filename

            # Check if already exists
            if filepath.exists():
                logger.debug(f"Action file already exists: {filename}")
                return None

            content = f"""---
type: whatsapp_message
source: whatsapp_watcher_playwright
priority: high
status: pending
created: {item['timestamp']}
---

# WhatsApp Message Detected

## From: {item['sender']}

## Message Content

{item['content']}

## Detected Keywords

{self._get_detected_keywords(item['content'])}

## Suggested Actions

- [ ] Review message context
- [ ] Check conversation history if needed
- [ ] Draft response if required
- [ ] Move to /Plans/ to create response
- [ ] Archive after processing

---

*Generated by WhatsApp Watcher (Playwright)*
"""

            filepath.write_text(content, encoding='utf-8')
            logger.info(f"Created action file: {filename}")

            # Log audit action
            self._log_audit_action("whatsapp_action_file_created", {
                "filename": filename,
                "message_id": item['id'],
                "sender": item['sender'],
                "has_keywords": self._get_detected_keywords(item['content'])
            })

            return filepath

        except Exception as e:
            logger.error(f"Error creating action file: {e}")
            return None

    def _get_detected_keywords(self, text: str) -> str:
        """Get list of detected keywords in message."""
        text_lower = text.lower()
        detected = [kw for kw in self.KEYWORDS if kw in text_lower]
        return ", ".join(detected) if detected else "None"

    def _log_audit_action(self, action_type: str, parameters: Dict[str, Any], result: str = "success") -> None:
        """
        Log audit action to the audit log.

        Args:
            action_type: Type of action performed
            parameters: Parameters of the action
            result: Result of the action (success/failed)
        """
        from utils.audit_logging import AuditLogger

        try:
            audit_logger = AuditLogger(self.vault_path)
            audit_logger.log_action(
                action_type=action_type,
                target="whatsapp",
                parameters=parameters,
                result=result
            )
        except Exception as e:
            logger.debug(f"Could not log audit action: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor WhatsApp Web for important messages (Playwright)"
    )

    parser.add_argument(
        "--vault",
        default=".",
        help="Path to Obsidian vault"
    )

    parser.add_argument(
        "--session",
        default="./whatsapp_session",
        help="Path to browser session directory"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Check interval in seconds (default: 30)"
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="Check once and exit"
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in headless mode (after first login)"
    )

    args = parser.parse_args()

    # Create watcher
    watcher = WhatsAppWatcherPlaywright(
        vault_path=args.vault,
        session_path=args.session,
        check_interval=args.interval,
        headless=args.headless
    )

    if args.once:
        # Check once
        print("\n" + "="*60)
        print("WHATSAPP WATCHER (Playwright) - One-Time Check")
        print("="*60)
        print(f"\nSession: {args.session}")
        print(f"Headless: {args.headless}")
        print("\n[*] Checking for messages...\n")

        messages = watcher.check_for_updates()

        print(f"\n[*] Found {len(messages)} important messages\n")

        for i, msg in enumerate(messages, 1):
            print(f"{i}. From: {msg['sender']}")
            print(f"   Content: {msg['content'][:80]}...")
            watcher.create_action_file(msg)
            print(f"   Created: WHATSAPP_{msg['id']}.md")
            print()

        print("="*60)
        print(f"Done! Created {len(messages)} action files")
        print("="*60)
    else:
        # Run continuous
        print("\n" + "="*60)
        print("WHATSAPP WATCHER (Playwright) - Continuous")
        print("="*60)
        print(f"\nSession: {args.session}")
        print(f"Check interval: {args.interval} seconds")
        print(f"Keywords: {', '.join(watcher.KEYWORDS)}")
        print("\n[*] Starting monitoring...")
        print("[*] Press Ctrl+C to stop\n")
        print("="*60 + "\n")

        watcher.run()


if __name__ == "__main__":
    main()
