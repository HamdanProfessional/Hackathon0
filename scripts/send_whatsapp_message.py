#!/usr/bin/env python3
"""
Send WhatsApp Message - Use Existing WhatsApp Session

Usage:
    python scripts/send_whatsapp_message.py "Contact Name" "Message"

Uses the same persistent Chrome session as the WhatsApp watcher.
"""
import sys
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

def send_whatsapp_message(contact, message, session_path=None):
    """Send WhatsApp message using existing WhatsApp session."""
    if session_path is None:
        # Use the same session as WhatsApp watcher
        vault_path = Path(__file__).parent.parent / "AI_Employee_Vault"
        session_path = vault_path / "whatsapp_session"

    session_path = Path(session_path)
    session_path.mkdir(parents=True, exist_ok=True)

    print(f"Sending WhatsApp message to {contact}...")
    print(f"Message: {message}")
    print("-" * 60)
    print(f"Using session: {session_path}")

    with sync_playwright() as p:
        # Launch with persistent session (same as WhatsApp watcher)
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(session_path),
            headless=False,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled'
            ]
        )

        try:
            # Get or create page
            if len(browser.pages) == 0:
                page = browser.new_page()
            else:
                page = browser.pages[0]

            # Navigate to WhatsApp Web
            print("Navigating to WhatsApp Web...")
            page.goto("https://web.whatsapp.com", wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)

            # Check if logged in (using query_selector instead of evaluate)
            chat_list = page.query_selector('[data-testid="chat-list"]')
            side = page.query_selector('#side')
            pane_side = page.query_selector('[data-testid="pane-side"]')
            is_logged_in = chat_list is not None or side is not None or pane_side is not None

            if not is_logged_in:
                print("Please scan the QR code in the browser window to log in...")
                try:
                    page.wait_for_selector('[data-testid="chat-list"], #side, [data-testid="pane-side"]', timeout=120000)
                    print("Logged in!")
                    page.wait_for_timeout(5000)
                except:
                    print("Login timeout. Please try again.")
                    return False
            else:
                print("Already logged in!")
                page.wait_for_timeout(5000)

            # Click on the contact directly in the chat list
            print(f"Searching for contact: {contact}...")

            # Try to find and click the contact by name
            # This is more reliable than using the search box
            try:
                # Look for the contact name in the chat list
                contact_xpath = f"//span[contains(text(), '{contact}')]"
                print(f"Looking for: {contact_xpath}")

                contact_element = page.wait_for_selector(f'text={contact}', timeout=10000)
                print(f"Found contact: {contact}")

                contact_element.click()
                page.wait_for_timeout(2000)
                print(f"Opened chat with {contact}")

            except Exception as e:
                print(f"Could not find contact '{contact}': {e}")
                print("Please check:")
                print("1. The exact contact name as it appears in WhatsApp")
                print("2. Make sure the contact is in your chat list")
                return False

            # Type message
            print("Sending message...")

            # Try multiple selectors for the message input
            message_selectors = [
                '[data-testid="conversation-panel-footer"] >> div[contenteditable="true"]',
                'div[contenteditable="true"][data-testid="true"]',
                '#main >> footer [contenteditable="true"]',
                'div[contenteditable="true"]'
            ]

            message_box = None
            for selector in message_selectors:
                try:
                    message_box = page.wait_for_selector(selector, timeout=5000)
                    print(f"Found message box with selector: {selector}")
                    break
                except:
                    continue

            if not message_box:
                print("Could not find message input. Trying alternative approach...")
                # Try typing directly into the focused element or using keyboard
                try:
                    # Click in the chat area to focus
                    page.click('#main')
                    page.wait_for_timeout(500)
                    # Type the message
                    page.keyboard.type(message)
                    page.wait_for_timeout(1000)
                except:
                    print("Could not type message")
                    return False
            else:
                message_box.fill(message)
                page.wait_for_timeout(500)

            # Send
            page.wait_for_timeout(500)  # Small delay before sending
            send_button = page.query_selector('[data-testid="send-button"]')
            if send_button:
                send_button.click()
                page.wait_for_timeout(2000)

            print(f"Message sent to {contact}!")
            print("Done!")

            # Keep browser open (WhatsApp watcher will use it)
            print("Browser left open for WhatsApp watcher to continue monitoring...")
            return True

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/send_whatsapp_message.py \"Contact Name\" \"Message\"")
        print("Example: python scripts/send_whatsapp_message.py \"Anus Mehmood\" \"Hi\"")
        print("\nNote: Uses the same WhatsApp session as the WhatsApp watcher")
        sys.exit(1)

    contact = sys.argv[1]
    message = sys.argv[2]

    success = send_whatsapp_message(contact, message)
    sys.exit(0 if success else 1)
