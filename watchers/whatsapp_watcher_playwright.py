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

        # Path to persistent state file (survives restarts)
        self.state_file = self.vault_path / '.whatsapp_state.json'

        # Load already processed messages from state file or existing files
        self._load_processed_messages()

        # Persistent browser context and page
        self.playwright = None
        self.browser = None
        self.page = None
        self._is_logged_in = False
        self._consecutive_login_failures = 0  # Track consecutive failures
        self._successful_checks = 0  # Track successful checks

        logger.info(f"WhatsApp watcher initialized with Playwright")
        logger.info(f"Session path: {self.session_path}")
        logger.info(f"State file: {self.state_file}")
        logger.info(f"Headless: {headless}")
        logger.info(f"Already processed: {len(self.processed_messages)} messages")

    def _load_processed_messages(self):
        """Load IDs of already processed messages from state file or existing action files."""
        import hashlib

        # Try loading from persistent state file first (fast and reliable)
        if self.state_file.exists():
            try:
                state_data = json.loads(self.state_file.read_text(encoding='utf-8'))
                loaded_ids = set(state_data.get('processed_messages', []))
                self.processed_messages.update(loaded_ids)
                logger.info(f"Loaded {len(loaded_ids)} processed messages from state file")
                return
            except Exception as e:
                logger.warning(f"Could not load state file: {e}")

        # Fallback: Scan all WhatsApp message files in the vault
        logger.info("State file not found, scanning existing WhatsApp files...")
        folders_to_scan = [
            self.needs_action,
            self.vault_path / 'Pending_Approval',
            self.vault_path / 'Approved',
            self.vault_path / 'Done'
        ]

        total_loaded = 0
        for folder in folders_to_scan:
            if not folder.exists():
                continue

            try:
                existing_files = list(folder.glob("WHATSAPP_*.md"))
                for filepath in existing_files:
                    content = filepath.read_text(encoding='utf-8')

                    # Extract sender and message content
                    sender = ""
                    message_content = ""

                    if '## From:' in content:
                        sender_part = content.split('## From:')[1].split('##')[0].strip()
                        sender = sender_part

                    if '## Message Content' in content:
                        message_content = content.split('## Message Content')[1].split('##')[0].strip()

                    # Generate hash using same method as runtime: sender + content[:100] (index-independent)
                    if sender and message_content:
                        content_hash = hashlib.md5((sender + message_content[:100]).encode()).hexdigest()[:8]
                        msg_id = f"WHATSAPP_MSG_{content_hash}"
                        self.processed_messages.add(msg_id)
                        total_loaded += 1

            except Exception as e:
                logger.debug(f"Could not scan folder {folder}: {e}")

        logger.info(f"Loaded {total_loaded} processed messages from existing files")

        # Save to state file for next time
        if total_loaded > 0:
            self._save_state()

    def _save_state(self):
        """Save processed messages to persistent state file."""
        try:
            state_data = {
                'processed_messages': list(self.processed_messages),
                'last_updated': datetime.now().isoformat()
            }
            self.state_file.write_text(json.dumps(state_data, indent=2), encoding='utf-8')
            logger.debug(f"Saved {len(self.processed_messages)} processed messages to state file")
        except Exception as e:
            logger.warning(f"Could not save state file: {e}")

    def _get_message_id(self, sender: str, content: str, index: int = None) -> str:
        """Generate a stable message ID based on content, not timestamp or index.

        IMPORTANT: Hash is index-independent since same message can be detected
        at different positions in different runs.
        """
        import hashlib
        # Create stable ID from sender + content hash only (NO index)
        # This ensures the same message always gets the same ID regardless of chat position
        content_hash = hashlib.md5((sender + content[:100]).encode()).hexdigest()[:8]
        return f"WHATSAPP_MSG_{content_hash}"

    def _start_browser(self):
        """Start the browser and keep it open for subsequent checks."""
        if self.browser is not None:
            return  # Already running

        try:
            self.playwright = sync_playwright().start()

            # Launch with persistent session
            self.browser = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled'
                ]
            )

            # Create page (or get existing)
            if len(self.browser.pages) == 0:
                self.page = self.browser.new_page()
            else:
                self.page = self.browser.pages[0]

            # Navigate to WhatsApp Web
            self.page.goto('https://web.whatsapp.com', timeout=60000)

            logger.info("✅ Browser started - WhatsApp Web loaded")

        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise

    def _stop_browser(self):
        """Close the browser and cleanup resources."""
        try:
            if self.browser:
                self.browser.close()
                self.browser = None
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
            self.page = None
            self._is_logged_in = False
            self._consecutive_login_failures = 0
            self._successful_checks = 0
            logger.info("Browser stopped")
        except Exception as e:
            logger.error(f"Error stopping browser: {e}")

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new unread WhatsApp messages.

        Returns:
            List of message dictionaries
        """
        messages = []

        try:
            # Start browser if not already running
            if self.browser is None:
                self._start_browser()
                # Wait for initial page load
                time.sleep(5)

            # Check if still logged in (only warn after multiple consecutive failures)
            login_ok = self._check_login_status()
            if not login_ok:
                self._consecutive_login_failures += 1
                # Only warn after 3 consecutive failures (avoid spam warnings)
                if self._consecutive_login_failures >= 3:
                    logger.warning(f"⚠️  Login check failing ({self._consecutive_login_failures} consecutive failures) - may need to re-login")
                # Still try to get messages anyway - the login check might be wrong
            else:
                # Reset failure counter on successful check
                if self._consecutive_login_failures > 0:
                    logger.info(f"✅ Login check recovered after {self._consecutive_login_failures} failures")
                self._consecutive_login_failures = 0

            # Get unread messages using persistent page
            logger.debug("Scanning for unread messages...")
            messages = self._get_unread_messages(self.page)

            # Track successful checks
            if messages is not None:
                self._successful_checks += 1
                # Reset failure counter if we successfully got messages
                if len(messages) > 0 or self._consecutive_login_failures > 0:
                    self._consecutive_login_failures = 0

        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            self._consecutive_login_failures += 1
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

    def _check_login_status(self) -> bool:
        """
        Check if still logged in to WhatsApp Web.

        Returns:
            True if logged in, False otherwise
        """
        try:
            # Check for logged-in indicators
            chat_selectors = [
                '[data-testid="chat-list"]',
                '#side > div',
                'div[role="application"]',
                '#pane-side'
            ]

            for selector in chat_selectors:
                if self.page.query_selector(selector):
                    if not self._is_logged_in:
                        logger.debug(f"✅ Confirmed logged in (found: {selector})")
                        self._is_logged_in = True
                    return True

            # Check if QR code is showing (not logged in) - use debug instead of warning
            qr_selectors = [
                'canvas[aria-label*="QR"]',
                'canvas[aria-label*="Scan"]',
                '[data-testid="qrcode"]',
                'div[data-refid="qrcode"]'
            ]

            for selector in qr_selectors:
                if self.page.query_selector(selector):
                    # Only log once, not every check
                    if self._consecutive_login_failures == 0:
                        logger.debug("⚠️  QR code detected - Please scan to login")
                    self._is_logged_in = False
                    return False

            self._is_logged_in = False
            return False

        except Exception as e:
            logger.debug(f"Error checking login status: {e}")
            self._is_logged_in = False
            return False

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

            # Use JavaScript to get clickable chat elements - very permissive approach
            chat_info = page.evaluate("""() => {
                // Try multiple selectors for the side panel
                const sideSelectors = ['#side', '[data-testid="conversation-panel"]', 'div[role="application"]'];
                let side = null;
                for (const selector of sideSelectors) {
                    side = document.querySelector(selector);
                    if (side) break;
                }

                if (!side) return {count: 0, selector: 'no-side'};

                // Try to find any clickable div that might be a chat
                const allDivs = Array.from(side.querySelectorAll('div'));

                // Very permissive filtering - just find clickable things with text
                const chatItems = allDivs.filter(el => {
                    const text = (el.innerText || '').trim();

                    // Skip empty elements
                    if (text.length < 2) return false;

                    // Skip single-line elements (likely not chats)
                    const lines = text.split('\\n').filter(l => l.trim().length > 0);
                    if (lines.length < 2) return false;

                    // Skip obvious non-chat elements
                    const lowerText = text.toLowerCase();
                    if (lowerText.includes('search') ||
                        lowerText.includes('type a message') ||
                        lowerText === 'whatsapp' ||
                        lowerText.includes('loading')) {
                        return false;
                    }

                    // Accept if it's clickable or has tabindex
                    return el.onclick !== null ||
                           el.getAttribute('tabindex') === '0' ||
                           el.getAttribute('role') === 'listitem' ||
                           el.getAttribute('role') === 'button' ||
                           el.tagName === 'A';
                });

                if (chatItems.length > 0) {
                    return {
                        count: chatItems.length,
                        selector: 'clickable-divs',
                        sampleTexts: chatItems.slice(0, 3).map(el => el.innerText.substring(0, 50))
                    };
                }

                return {count: 0, selector: 'no-clickable', totalDivs: allDivs.length};
            }""")

            logger.info(f"Chat detection: {chat_info}")
            chat_count = chat_info.get('count', 0)

            logger.info(f"Found {chat_count} chat elements via JavaScript")

            if chat_count == 0:
                logger.warning("Could not find any chats - using fallback direct query")

                # Fallback: Try direct Playwright query selectors
                chat_selectors = [
                    '[data-testid="chat-list"] > div',
                    'div[role="listitem"]',
                    '[role="listitem"]'
                ]

                for selector in chat_selectors:
                    chats = page.query_selector_all(selector)
                    logger.info(f"Direct query '{selector}' found {len(chats)} elements")
                    if len(chats) > 0:
                        chat_count = len(chats)
                        break

                if chat_count == 0:
                    logger.warning("Could not find any chats with any method")
                    return messages

            # Limit to first 10 recent chats
            chats_to_check = min(10, chat_count)
            logger.info(f"Checking last {chats_to_check} chats for keywords: {', '.join(self.KEYWORDS)}")

            # NEW: First check chat list preview for keywords (faster, no clicking needed)
            logger.info("Phase 1: Scanning chat list previews for keywords...")
            preview_info = page.evaluate("""() => {
                const side = document.querySelector('#side');
                if (!side) return {found: 0, messages: []};

                // Get all clickable divs (same as detection)
                const allDivs = Array.from(side.querySelectorAll('div'));
                const chatItems = allDivs.filter(el => {
                    const text = (el.innerText || '').trim();
                    if (text.length < 2) return false;
                    const lines = text.split('\\n').filter(l => l.trim().length > 0);
                    if (lines.length < 2) return false;
                    const lowerText = text.toLowerCase();
                    if (lowerText.includes('search') ||
                        lowerText.includes('type a message') ||
                        lowerText === 'whatsapp' ||
                        lowerText.includes('loading')) {
                        return false;
                    }
                    return el.onclick !== null ||
                           el.getAttribute('tabindex') === '0' ||
                           el.getAttribute('role') === 'listitem';
                });

                // Check each chat's preview text for keywords
                const foundMessages = [];
                const keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'watch'];

                chatItems.forEach((chat, index) => {
                    const text = chat.innerText || '';
                    const lines = text.split('\\n');
                    const firstLine = lines[0] || '';

                    // Check if any keyword is in the preview text
                    const foundKeyword = keywords.find(kw => text.toLowerCase().includes(kw));
                    if (foundKeyword) {
                        // Get the line containing the keyword, not just the last line
                        const lineWithKeyword = lines.find(line => line.toLowerCase().includes(foundKeyword)) || '';

                        if (lineWithKeyword) {
                            foundMessages.push({
                                index: index,
                                sender: firstLine.substring(0, 50),
                                content: lineWithKeyword,
                                keyword: foundKeyword
                            });
                        }
                    }
                });

                return {
                    found: foundMessages.length,
                    messages: foundMessages,
                    total: chatItems.length
                };
            }""")

            logger.info(f"Preview scan found {preview_info.get('found', 0)} messages with keywords")

            # If we found messages in previews, create action files directly without clicking
            if preview_info.get('found', 0) > 0:
                for msg_data in preview_info.get('messages', []):
                    # Use stable ID based on content
                    msg_id = self._get_message_id(msg_data['sender'], msg_data['content'], msg_data['index'])
                    if msg_id not in self.processed_messages:
                        self.processed_messages.add(msg_id)
                        self._save_state()  # Persist after adding new message

                        messages.append({
                            'id': msg_id,
                            'sender': msg_data['sender'],
                            'content': msg_data['content'],
                            'timestamp': datetime.now().isoformat(),
                            'index': msg_data['index'],
                            'source': 'chat_preview'
                        })

                        logger.info(f"✅ FOUND '{msg_data['keyword']}'\" in chat preview from {msg_data['sender']}!")

                # If we found something, no need to click into chats
                if len(messages) > 0:
                    logger.info(f"✅ Found {len(messages)} messages via preview scan - skipping deep scan")
                    return messages

            # Otherwise, proceed with clicking into chats
            logger.info("Phase 2: No keywords found in previews, clicking into chats...")

            for i in range(chats_to_check):
                try:
                    logger.info(f"--- Processing chat {i} ---")

                    # Simple click approach - just click the element directly
                    clicked = page.evaluate(f"""(index) => {{
                        const side = document.querySelector('#side');
                        if (!side) return false;

                        // Get all clickable divs
                        const allDivs = Array.from(side.querySelectorAll('div'));

                        // Very permissive filtering - same as detection
                        const chatItems = allDivs.filter(el => {{
                            const text = (el.innerText || '').trim();
                            if (text.length < 2) return false;
                            const lines = text.split('\\n').filter(l => l.trim().length > 0);
                            if (lines.length < 2) return false;
                            const lowerText = text.toLowerCase();
                            if (lowerText.includes('search') ||
                                lowerText.includes('type a message') ||
                                lowerText === 'whatsapp' ||
                                lowerText.includes('loading')) {{
                                return false;
                            }}
                            return el.onclick !== null ||
                                   el.getAttribute('tabindex') === '0' ||
                                   el.getAttribute('role') === 'listitem' ||
                                   el.getAttribute('role') === 'button' ||
                                   el.tagName === 'A';
                        }});

                        if (chatItems.length > 0 && index < chatItems.length) {{
                            chatItems[index].scrollIntoView();

                            // Try multiple click methods
                            try {{
                                chatItems[index].click();
                            }} catch (e) {{
                                // Try clicking with dispatch
                                chatItems[index].dispatchEvent(new MouseEvent('click', {{
                                    bubbles: true,
                                    cancelable: true,
                                    view: window
                                }}));
                            }}

                            return {{ success: true, element: chatItems[index].tagName }};
                        }}

                        return {{ success: false, error: 'index out of range' }};
                    }}""", i)

                    if not clicked or not clicked.get('success'):
                        logger.warning(f"Could not click chat {i}")
                        continue

                    logger.info(f"Clicked chat {i}, waiting for load...")
                    time.sleep(3.0)  # Wait even longer for chat to load

                    # Get sender name first
                    sender = self._get_sender_name(page)
                    logger.info(f"Sender: {sender}")

                    # Try multiple message selectors
                    chat_messages = page.query_selector_all('[data-testid="msg-container"], [data-testid="msg"], div[class*="message"]')

                    # DEBUG: Check if we're actually in a chat
                    chat_content = page.evaluate("""() => {
                        const main = document.querySelector('#main');
                        if (!main) return 'No main element';

                        const messages = main.querySelectorAll('[data-testid="msg-container"], [data-testid="msg"]');
                        const text = main.innerText || '';
                        return {
                            mainExists: true,
                            msgContainers: messages.length,
                            innerText: text.substring ? text.substring(0, 200) : 'No text'
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
                                # Use stable ID based on content
                                msg_id = self._get_message_id(sender, msg_text, i)

                                if msg_id not in self.processed_messages:
                                    self.processed_messages.add(msg_id)
                                    self._save_state()  # Persist after adding new message

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

                    # If no messages found with specific selectors, try getting all text from the chat panel
                    if not messages and chat_content.get('innerText'):
                        # The chat panel is open but no message containers found
                        full_text = chat_content.get('innerText', '')
                        if full_text and len(full_text) > 0:
                            logger.info(f"No message containers found, but chat panel has {len(full_text)} characters of text")
                            # Try to extract messages from the full text
                            lines = full_text.split('\n')
                            current_sender = sender

                            for line in lines:
                                if self._is_important(line):
                                    msg_id = self._get_message_id(current_sender, line, i)
                                    if msg_id not in self.processed_messages:
                                        self.processed_messages.add(msg_id)
                                        self._save_state()  # Persist after adding new message

                                        messages.append({
                                            'id': msg_id,
                                            'sender': current_sender,
                                            'content': line.strip(),
                                            'timestamp': datetime.now().isoformat(),
                                            'index': i
                                        })

                                        logger.info(f"✓✓✓ FOUND KEYWORD in full chat text!")
                                        break  # Only take first match from each chat

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

    def run(self):
        """
        Run the watcher with continuous monitoring.
        Overrides base run method to ensure browser cleanup.
        """
        import signal

        def cleanup_handler(signum, frame):
            logger.info("Received interrupt signal, cleaning up...")
            self._stop_browser()
            sys.exit(0)

        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, cleanup_handler)
        if hasattr(signal, 'SIGBREAK'):
            signal.signal(signal.SIGBREAK, cleanup_handler)

        try:
            # Start browser once at the beginning
            logger.info("Starting WhatsApp watcher (persistent browser mode)")
            self._start_browser()
            logger.info("Browser started - will remain open for all checks")

            # Wait for WhatsApp Web to fully load
            logger.info("Waiting 10 seconds for WhatsApp Web to fully load...")
            time.sleep(10)

            # Check initial login status - use debug instead of warning
            if self._check_login_status():
                logger.info("✅ Confirmed logged in - starting message monitoring")
            else:
                logger.debug("⚠️  Login status uncertain - will monitor and attempt anyway")

            # Call parent run method which has the main loop
            super().run()

        except KeyboardInterrupt:
            logger.info("Watcher stopped by user")
        finally:
            # Always cleanup on exit
            logger.info("Cleaning up browser resources...")
            self._stop_browser()


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
