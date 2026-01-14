#!/usr/bin/env python3
"""
Manual Debug WhatsApp Watcher - Wait for user to confirm login
"""

import time
from playwright.sync_api import sync_playwright

print("\n" + "="*60)
print("WHATSAPP DEBUG - MANUAL MODE")
print("="*60)
print("\n1. Browser will open WhatsApp Web")
print("2. Scan the QR code with your phone")
print("3. Type 'done' and press Enter when you see your chats")
print("="*60 + "\n")

with sync_playwright() as p:
    # Launch with persistent session
    browser = p.chromium.launch_persistent_context(
        user_data_dir="./whatsapp_session",
        headless=False,
        args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
    )

    if len(browser.pages) == 0:
        page = browser.new_page()
    else:
        page = browser.pages[0]

    print("Opening WhatsApp Web...")
    page.goto('https://web.whatsapp.com')

    # Wait for user to scan QR
    input("\n👆 Press Enter after you've scanned the QR code and see your chats...")

    # Check if we're logged in
    try:
        chat_list = page.query_selector('[data-testid="chat-list"]')
        if chat_list:
            print("✅ Successfully connected to WhatsApp Web!\n")

            # Get all chats
            all_chats = page.query_selector_all('div[role="listitem"]')
            print(f"Total chats found: {len(all_chats)}\n")

            keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'watch']
            messages_found = []

            print("Scanning chats for keywords...")
            print("-" * 60)

            for i, chat in enumerate(all_chats[:15]):
                try:
                    chat.click()
                    time.sleep(0.5)

                    # Get messages
                    messages = page.query_selector_all('[data-testid="msg-container"]')

                    # Check last few messages
                    for msg in messages[-2:]:
                        try:
                            msg_text = msg.inner_text()
                            msg_text_lower = msg_text.lower()

                            for kw in keywords:
                                if kw in msg_text_lower:
                                    # Get sender name
                                    title_elem = page.query_selector('[data-testid="chat-title"]')
                                    sender = title_elem.inner_text() if title_elem else "Unknown"

                                    messages_found.append({
                                        'sender': sender,
                                        'keyword': kw,
                                        'text': msg_text[:150]
                                    })

                                    print(f"\n✓ Found '{kw}' in message from {sender}:")
                                    print(f"  {msg_text[:100]}...")
                        except:
                            pass

                    # Go back to chat list
                    page.go_back()
                    time.sleep(0.3)

                except Exception as e:
                    continue

            print("\n" + "="*60)
            print(f"TOTAL MESSAGES WITH KEYWORDS: {len(messages_found)}")
            print("="*60 + "\n")

        else:
            print("❌ Chat list not found - may not be logged in properly")
    except Exception as e:
        print(f"Error: {e}")

    print("\nBrowser will stay open for 60 seconds for inspection...")
    time.sleep(60)

    browser.close()
    print("\n✅ Debug session complete")
