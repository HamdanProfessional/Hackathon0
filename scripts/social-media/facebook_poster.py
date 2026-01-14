#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Poster - Direct posting to facebook.com using Playwright

Posts directly to facebook.com using Playwright with CDP connection.
Uses fast copy-paste method for quick posting.

Usage:
    python facebook_poster.py "Your post content here"
    python facebook_poster.py "Your post content here" --live
"""

import argparse
import os
import random
import time
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    print("Playwright not installed. Run: pip install playwright")
    sys.exit(1)


# ==================== CONFIGURATION ====================

# DRY_RUN: Set to False to actually publish posts
DRY_RUN = os.getenv('FACEBOOK_DRY_RUN', 'true').lower() == 'true'

FACEBOOK_URL = "https://facebook.com"
CDP_ENDPOINT = "http://localhost:9222"

# Page load delays
INITIAL_PAGE_LOAD_DELAY = 3.0


# ==================== MAIN ====================

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Post to Facebook directly')
    parser.add_argument('content', help='Post content')
    parser.add_argument('--live', action='store_true', help='Actually publish (not dry-run)')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (preview only)')

    args = parser.parse_args()

    # Override dry run if specified
    global DRY_RUN
    if args.live:
        DRY_RUN = False
    elif args.dry_run:
        DRY_RUN = True

    print("\n" + "="*60)
    print("FACEBOOK POSTER - Direct to facebook.com")
    print("="*60)
    print(f"Content: {args.content[:100]}...")
    print(f"Mode: {'LIVE' if not DRY_RUN else 'DRY RUN'}")
    print("="*60 + "\n")

    if DRY_RUN:
        print("DRY RUN MODE: Preview only, will not publish\n")

    try:
        with sync_playwright() as p:
            # Connect to existing Chrome via CDP
            print("Connecting to Chrome CDP...")
            print(f"CDP Endpoint: {CDP_ENDPOINT}")

            try:
                browser = p.chromium.connect_over_cdp(CDP_ENDPOINT)
                print("Connected to Chrome!\n")

                # Get or create page
                contexts = browser.contexts
                if contexts:
                    context = contexts[0]
                    pages = context.pages
                    if pages:
                        page = pages[0]
                    else:
                        page = context.new_page()
                else:
                    print("No browser context found")
                    return False

                print(f"Current URL: {page.url}")

                # Navigate to Facebook home/feed if not already there
                if 'facebook.com' not in page.url or '/events' in page.url or '/groups' in page.url:
                    print(f"\nNavigating to Facebook home page...")
                    page.goto("https://www.facebook.com/", wait_until='domcontentloaded', timeout=30000)
                    print("Page loaded")
                    time.sleep(2)
                else:
                    print("Already on Facebook home")

                # Wait a moment for page to be ready
                time.sleep(2)

                # Use JavaScript to find and interact with post box
                print("\nLooking for post box using JavaScript...")

                # First, try to find and click "What's on your mind?" text/area
                find_and_click_composer_js = '''
                () => {
                    // Approach 1: Find "What's on your mind?" text and click near it
                    const allElements = document.querySelectorAll('*');
                    for (let elem of allElements) {
                        const text = elem.textContent || elem.innerText || '';
                        if (text.includes("What's on your mind") || text.includes("What's on your mind,")) {
                            // Found the text, now find the clickable area
                            let clickable = elem;
                            while (clickable && clickable.tagName !== 'BODY') {
                                if (clickable.getAttribute('role') === 'textbox' ||
                                    clickable.getAttribute('contenteditable') === 'true' ||
                                    clickable.tagName === 'TEXTAREA' ||
                                    clickable.onclick) {
                                    clickable.click();
                                    return {
                                        found: true,
                                        method: 'click-composer',
                                        element: clickable.tagName
                                    };
                                }
                                clickable = clickable.parentElement;
                            }
                        }
                    }

                    // Approach 2: Find any element with "What's on your mind" in aria-label
                    const labeledElements = document.querySelectorAll('[aria-label*="What"]');
                    for (let elem of labeledElements) {
                        if (elem.getAttribute('aria-label').includes('What')) {
                            elem.click();
                            return {
                                found: true,
                                method: 'click-labeled',
                                ariaLabel: elem.getAttribute('aria-label')
                            };
                        }
                    }

                    // Approach 3: Find contenteditable elements
                    const editables = document.querySelectorAll('[contenteditable="true"]');
                    if (editables.length > 0) {
                        editables[0].focus();
                        return {
                            found: true,
                            method: 'focus-editable',
                            count: editables.length
                        };
                    }

                    return { found: false, method: 'none' };
                }
                '''

                result = page.evaluate(find_and_click_composer_js)
                print(f"Composer search result: {result}")

                if not result.get('found'):
                    print("⚠️  Could not find 'What's on your mind?' box")
                    print("⚠️  Trying to click on page center...")

                    # Click in center of page to activate
                    page.mouse.click(400, 300)
                    time.sleep(2)

                    # Try again
                    result = page.evaluate(find_and_click_composer_js)
                    print(f"Second attempt result: {result}")

                if not result.get('found'):
                    print("❌ Still cannot find post box")
                    print("⚠️  Please make sure you're logged into Facebook")
                    print("⚠️  And that you can see the 'What's on your mind?' box")
                    return False

                print(f"\n✅ Found post box using: {result.get('method')}")
                time.sleep(1)

                # Now paste the content
                paste_js = f'''
                () => {{
                    // Try to find the active/focused element
                    let elem = document.activeElement;

                    // If active element isn't editable, find an editable one
                    if (!elem.getAttribute('contenteditable') && elem.tagName !== 'TEXTAREA') {{
                        const editables = document.querySelectorAll('[contenteditable="true"], textarea');
                        if (editables.length > 0) {{
                            elem = editables[0];
                            elem.focus();
                        }}
                    }}

                    if (!elem) return {{ success: false, error: 'no editable element' }};

                    // Paste content
                    navigator.clipboard.writeText("{escape_js_string(args.content)}")
                        .then(() => {{
                            document.execCommand('paste');
                            return {{ success: true }};
                        }})
                        .catch(err => {{
                            // Fallback: set innerText directly
                            elem.innerText = "{escape_js_string(args.content)}";
                            // Trigger input event
                            const event = new Event('input', {{ bubbles: true }});
                            elem.dispatchEvent(event);
                            return {{ success: true, fallback: true }};
                        }});
                }}
                '''

                paste_result = page.evaluate(paste_js)
                print(f"Paste result: {paste_result}")

                if paste_result and (paste_result.get('success') or paste_result.get('fallback')):
                    print("✅ Content added successfully!")
                elif paste_result is None:
                    print("⚠️  Paste returned None - trying direct method...")
                    # Direct approach - type full content slowly
                    print("Typing full content...")
                    page.keyboard.type(args.content)  # Type full content, not partial
                    print("✅ Content typed successfully")
                else:
                    print(f"⚠️  Paste had issues: {paste_result}")
                    return False

                if not DRY_RUN:
                    print("\n" + "="*60)
                    print("Waiting 5 seconds for you to review the post...")
                    print("Then auto-publishing...")
                    print("="*60)

                    # Wait for user to review
                    time.sleep(5)

                    # Look for Post button and check if it's enabled
                    print("Looking for Post button...")

                    # First, let's check if we can find the Post button and its status
                    check_button_js = '''
                    () => {
                        // Use the selector provided by user: aria-label="Post" with role="button"
                        const button = document.querySelector('[aria-label="Post"][role="button"]');

                        if (button) {
                            const role = button.getAttribute('role');
                            const classList = button.className || '';
                            const tabIndex = button.getAttribute('tabindex');

                            return {
                                found: true,
                                role: role,
                                disabled: role === 'none',
                                hasTabindex: tabIndex,
                                classList: classList.substring(0, 100),
                                ariaLabel: button.getAttribute('aria-label'),
                                id: button.id
                            };
                        }

                        return { found: false };
                    }
                    '''

                    check_result = page.evaluate(check_button_js)
                    print(f"Button check result: {check_result}")

                    if check_result.get('found'):
                        if check_result.get('disabled'):
                            print("⚠️  Post button is DISABLED")
                            print("   This means Facebook needs more interaction")
                            print("\n📋 Please review the post in Chrome:")
                            print("   1. Check the content is correct")
                            print("   2. Click the Post button manually")
                            print("   3. The button should be enabled now")
                        else:
                            print("✅ Post button is enabled!")

                            # Try clicking using multiple methods
                            print("Attempting to click...")

                            click_methods = '''
                            () => {
                                const svgs = document.querySelectorAll('svg[viewBox="0 0 20 20"]');

                                for (let svg of svgs) {
                                    const paths = svg.querySelectorAll('path');
                                    if (paths.length > 0) {
                                        const d = paths[0].getAttribute('d');
                                        if (d && (d.includes('M17.99') || d.includes('M11.238'))) {
                                            let button = svg.closest('div');

                                            // Method 1: Direct click
                                            try {
                                                button.click();
                                            return { method: 'direct-click', success: true };
                                            } catch(e) {}

                                            // Method 2: Mouse event
                                            try {
                                                const event = new MouseEvent('click', {
                                                    view: window,
                                                    bubbles: true,
                                                    cancelable: true
                                                });
                                                button.dispatchEvent(event);
                                                return { method: 'mouse-event', success: true };
                                            } catch(e) {}

                                            // Method 3: Focus + Enter
                                            try {
                                                button.focus();
                                                document.execCommand('insertText', false, null);
                                                return { method: 'focus-enter', success: true };
                                            } catch(e) {}
                                        }
                                    }
                                }

                                return { method: 'none', success: false };
                            }
                            '''

                            click_result = page.evaluate(click_methods)
                            print(f"Click result: {click_result}")

                            if click_result.get('success'):
                                print("✅ Post button clicked!")
                            else:
                                print("⚠️  Could not click Post button")
                                print("   Please click Post manually in Chrome")
                    else:
                        print("⚠️  Could not find Post button")
                        print("   Please click Post manually in Chrome")
                else:
                    print("\n" + "="*60)
                    print("DRY RUN COMPLETE - Post previewed (not published)")
                    print("="*60)

                browser.close()
                return True

            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()
                return False

    except Exception as e:
        print(f"Failed to connect to Chrome: {e}")
        print(f"\nMake sure Chrome is running with:")
        print(f"chrome.exe --remote-debugging-port=9222")
        return False


def escape_js_string(text: str) -> str:
    """Escape special characters for JavaScript."""
    return (text
            .replace('\\', '\\\\')
            .replace('"', '\\"')
            .replace('\n', '\\n')
            .replace('\r', '')
            .replace('\t', '\\t'))


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
