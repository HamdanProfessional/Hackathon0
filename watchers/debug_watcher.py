#!/usr/bin/env python3
"""
Debug WhatsApp Watcher - Keep browser open to see what's happening
"""

import time
from playwright.sync_api import sync_playwright

def debug_whatsapp():
    """Debug WhatsApp to see what selectors work."""

    with sync_playwright() as p:
        # Launch with persistent session (stays logged in)
        browser = p.chromium.launch_persistent_context(
            user_data_dir="./whatsapp_session",
            headless=False,  # Keep browser visible
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )

        # Create page
        if len(browser.pages) == 0:
            page = browser.new_page()
        else:
            page = browser.pages[0]

        # Navigate to WhatsApp Web
        print("Navigating to WhatsApp Web...")
        page.goto('https://web.whatsapp.com', timeout=60000)

        # Wait for chat list
        try:
            page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
            print("✅ Connected to WhatsApp Web")
            print("\n=== Checking for unread messages ===\n")

            # Try different selectors to find unread messages
            selectors_to_try = [
                ('[data-testid="unread"]', 'Standard unread selector'),
                ('[data-icon="unread"]', 'Unread icon'),
                ('.unread', 'Unread class'),
                ('[aria-label*="unread"]', 'Aria label unread'),
                ('[data-testid="chat-list"] li', 'All chat list items'),
            ]

            for selector, description in selectors_to_try:
                try:
                    elements = page.query_selector_all(selector)
                    print(f"✓ {description}: Found {len(elements)} elements")
                except Exception as e:
                    print(f"✗ {description}: Error - {e}")

            # Get all chat list items and check their text
            print("\n=== Scanning all chats for keywords ===")
            chats = page.query_selector_all('[data-testid="chat-list"] > div')
            print(f"Total chats: {len(chats)}")

            keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'watch']
            messages_with_keywords = []

            for i, chat in enumerate(chats[:20]):  # Check first 20
                try:
                    # Click on chat
                    chat.click()
                    time.sleep(0.5)

                    # Get all messages in this chat
                    messages = page.query_selector_all('[data-testid="msg-container"]')

                    for msg in messages[-3:]:  # Check last 3 messages
                        text = msg.inner_text().lower()
                        if any(kw in text for kw in keywords):
                            messages_with_keywords.append({
                                'chat_index': i,
                                'text': text[:100]
                            })
                            print(f"Found keyword in chat {i}: {text[:80]}...")

                except Exception as e:
                    continue

            print(f"\n=== Summary ===")
            print(f"Messages with keywords: {len(messages_with_keywords)}")

            # Keep browser open for inspection
            print("\nBrowser will stay open for 60 seconds for inspection...")
            time.sleep(60)

        except Exception as e:
            print(f"Error: {e}")
            print("Keeping browser open for 30 seconds...")
            time.sleep(30)

        browser.close()

if __name__ == "__main__":
    debug_whatsapp()
