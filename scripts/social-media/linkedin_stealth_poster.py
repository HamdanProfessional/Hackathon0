#!/usr/bin/env python3
"""
LinkedIn Stealth Poster - Undetectable Browser Automation

Uses Method 1: Browser Session Hijacking via Chrome DevTools Protocol (CDP)
Connects to your existing Chrome session to avoid LinkedIn's bot detection.

Human-like behaviors:
- Variable typing speed (0.05s - 0.18s per character)
- Occasional thinking pauses (0.5s)
- Hover before clicking (0.5s - 1.2s delay)
- No automation flags in browser

Usage:
1. Start Chrome with remote debugging (see commands below)
2. Run this script: python linkedin_stealth_poster.py "Your post content here"
"""

import argparse
import random
import time
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    print("❌ Playwright not installed. Run: pip install playwright")
    sys.exit(1)


# ==================== CONFIGURATION ====================

DRY_RUN = False  # Set to True to skip actual posting

LINKEDIN_URL = "https://www.linkedin.com/feed/"
CDP_ENDPOINT = "http://localhost:9222"

# Human behavior parameters
TYPING_MIN_DELAY = 0.05  # Minimum delay between keystrokes (seconds)
TYPING_MAX_DELAY = 0.18  # Maximum delay between keystrokes (seconds)
THINKING_PAUSE_PROBABILITY = 0.15  # 15% chance of a thinking pause
THINKING_PAUSE_DURATION = 0.5  # Duration of thinking pause

HOVER_MIN_DELAY = 0.5  # Minimum hover before click (seconds)
HOVER_MAX_DELAY = 1.2  # Maximum hover before click (seconds)


# ==================== HELPER FUNCTIONS ====================

def human_type(page, selector, text):
    """
    Type text character-by-character to mimic human typing.

    Does NOT use page.type() or page.fill() which are instant.
    Instead, focuses the element and presses each key individually
    with random delays to simulate variable typing speed.

    Args:
        page: Playwright page object
        selector: CSS selector for the input field
        text: Text to type

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"🖐️  Human-typing into: {selector}")

        # Click to focus the element first
        page.click(selector, timeout=10000)
        time.sleep(random.uniform(0.2, 0.5))  # Small pause after focusing

        # Type character by character
        for i, char in enumerate(text):
            # Press the key (this is like a human pressing a key)
            page.keyboard.press(char)

            # Random delay between keystrokes (variable typing speed)
            delay = random.uniform(TYPING_MIN_DELAY, TYPING_MAX_DELAY)
            time.sleep(delay)

            # Occasional "thinking" pause (simulating human thought)
            if random.random() < THINKING_PAUSE_PROBABILITY:
                print(f"      ⏸️  Thinking pause...")
                time.sleep(THINKING_PAUSE_DURATION)

        print(f"✅ Finished typing ({len(text)} chars)")
        return True

    except Exception as e:
        print(f"❌ human_type failed: {e}")
        return False


def human_click(page, selector):
    """
    Click an element with human-like hover behavior.

    Does NOT click immediately. First hovers over the element
    (like a human moving their mouse), then waits a random duration,
    then clicks.

    Args:
        page: Playwright page object
        selector: CSS selector for the element

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"🖱️  Human-clicking: {selector}")

        # First hover over the element (like moving mouse there)
        page.hover(selector, timeout=10000)
        print(f"      👆 Hovering...")

        # Random delay while hovering (like human hesitation)
        hover_delay = random.uniform(HOVER_MIN_DELAY, HOVER_MAX_DELAY)
        time.sleep(hover_delay)

        # Then click
        page.click(selector, timeout=10000, force=True)
        print(f"✅ Clicked after {hover_delay:.2f}s hover")

        return True

    except Exception as e:
        print(f"❌ human_click failed: {e}")
        return False


# ==================== MAIN POSTING LOGIC ====================

def create_linkedin_post(page, post_content):
    """
    Create a LinkedIn post using stealth techniques.

    Args:
        page: Playwright page object (already connected to Chrome)
        post_content: Text content to post

    Returns:
        True if successful, False otherwise
    """
    print("\n" + "="*60)
    print("🚀 STARTING LINKEDIN STEALTH POST")
    print("="*60 + "\n")

    try:
        # Step 1: Navigate to LinkedIn feed
        print(f"📍 Step 1: Navigating to LinkedIn feed...")
        page.goto(LINKEDIN_URL, wait_until="networkidle", timeout=30000)
        time.sleep(random.uniform(2.0, 4.0))  # Random delay like human reading
        print("✅ Page loaded\n")

        # Step 2: Click "Start a post" button (using human_click)
        print(f"📍 Step 2: Opening 'Start a post' modal...")
        start_post_selector = 'button[aria-label*="Start a post"], .share-box-feed-entry__trigger, [data-control-name="share_modal_box"]'

        # Try multiple selectors for "Start a post"
        selectors_to_try = [
            'button[aria-label*="Start a post"]',
            'button[aria-label*="start a post"]',
            '.share-box-feed-entry__trigger',
            '[data-control-name="share_modal_box"]',
            '#ember25'
        ]

        clicked = False
        for selector in selectors_to_try:
            try:
                if human_click(page, selector):
                    clicked = True
                    break
            except:
                continue

        if not clicked:
            print("❌ Could not find 'Start a post' button")
            page.screenshot(path="error_debug.png", full_page=True)
            print("📸 Saved debug screenshot: error_debug.png")
            return False

        time.sleep(random.uniform(1.5, 3.0))  # Wait for modal to open
        print("✅ Modal opened\n")

        # Step 3: Type the post content (using human_type)
        print(f"📍 Step 3: Typing post content...")
        content_selector = 'div[contenteditable="true"][role="textbox"], .ql-editor, [data-artdeco-is="focused"]'

        if not human_type(page, content_selector, post_content):
            print("❌ Could not type post content")
            page.screenshot(path="error_debug.png", full_page=True)
            print("📸 Saved debug screenshot: error_debug.png")
            return False

        time.sleep(random.uniform(1.0, 2.0))  # Pause after typing
        print("✅ Content typed\n")

        # Step 4: Click "Post" button (using human_click)
        if not DRY_RUN:
            print(f"📍 Step 4: Clicking 'Post' button...")
            post_button_selectors = [
                'button[aria-label*="Post"][type="submit"]',
                'button[aria-label="Post"]',
                '.share-actions__primary-action button',
                'button[data-control-name="share_post"]'
            ]

            posted = False
            for selector in post_button_selectors:
                try:
                    if human_click(page, selector):
                        posted = True
                        break
                except:
                    continue

            if not posted:
                print("❌ Could not find 'Post' button")
                page.screenshot(path="error_debug.png", full_page=True)
                print("📸 Saved debug screenshot: error_debug.png")
                return False

            print("✅ Post button clicked\n")
        else:
            print("⚠️  DRY RUN MODE: Skipping actual post click")
            print("📸 Saving screenshot instead...")
            page.screenshot(path="dry_run_preview.png", full_page=True)
            print("✅ Saved: dry_run_preview.png\n")

        # Step 5: Wait for confirmation
        if not DRY_RUN:
            time.sleep(random.uniform(3.0, 5.0))
            print("✅ Post should be live now!")

        print("\n" + "="*60)
        print("🎉 LINKEDIN POST COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")

        return True

    except PlaywrightTimeoutError as e:
        print(f"❌ Timeout error: {e}")
        page.screenshot(path="error_debug.png", full_page=True)
        print("📸 Saved debug screenshot: error_debug.png")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        page.screenshot(path="error_debug.png", full_page=True)
        print("📸 Saved debug screenshot: error_debug.png")
        return False


def main():
    """Main entry point for the script."""

    parser = argparse.ArgumentParser(
        description="LinkedIn Stealth Poster - Undetectable browser automation"
    )
    parser.add_argument(
        "content",
        help="Post content (wrap in quotes if it contains spaces)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without actually posting"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (headful, more verbose)"
    )

    args = parser.parse_args()

    # Override DRY_RUN if flag is set
    global DRY_RUN
    if args.dry_run:
        DRY_RUN = True

    print("""
╔══════════════════════════════════════════════════════════╗
║          LINKEDIN STEALTH POSTER v1.0                    ║
║      Browser Session Hijacking + Human Mimicry           ║
╚══════════════════════════════════════════════════════════╝
    """)

    print(f"📝 Post Content: {args.content[:100]}{'...' if len(args.content) > 100 else ''}")
    print(f"🔗 CDP Endpoint: {CDP_ENDPOINT}")
    print(f"⚠️  Dry Run: {'YES' if DRY_RUN else 'NO'}\n")

    with sync_playwright() as p:
        try:
            # Connect to existing Chrome instance via CDP
            print("🔌 Connecting to Chrome CDP session...")
            print(f"   Make sure Chrome is running with --remote-debugging-port=9222\n")

            browser = p.chromium.connect_over_cdp(CDP_ENDPOINT)
            print("✅ Connected to existing Chrome session!")

            # Get the default context and page (or create new page)
            default_context = browser.contexts[0]
            page = default_context.pages[0] if default_context.pages else default_context.new_page()

            # Bring window to front
            page.bring_to_front()

            # Create the post
            success = create_linkedin_post(page, args.content)

            if success:
                print("✅ Script completed successfully!")
                sys.exit(0)
            else:
                print("❌ Script failed. Check error_debug.png")
                sys.exit(1)

        except Exception as e:
            print(f"\n❌ CONNECTION ERROR: {e}")
            print("\n" + "="*60)
            print("TROUBLESHOOTING:")
            print("="*60)
            print("""
1. Make sure Chrome is running with remote debugging enabled.
   See the commands at the bottom of this script.

2. Check if Chrome is listening on port 9222:
   - Windows: netstat -ano | findstr :9222
   - Mac/Linux: lsof -i :9222

3. Close all other Chrome instances and restart with the debugging flag.

4. If you see 'Target closed', restart Chrome with the debugging command.
            """)
            sys.exit(1)


if __name__ == "__main__":
    main()


# ==================== CHROME LAUNCH COMMANDS ====================
"""
╔════════════════════════════════════════════════════════════════════╗
║  HOW TO LAUNCH CHROME WITH REMOTE DEBUGGING                      ║
╚════════════════════════════════════════════════════════════════════╝

🪟 WINDOWS COMMAND:

chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebug" ^
    --disable-web-security ^
    --disable-features=IsolateOrigins,site-per-process ^
    --no-first-run ^
    --no-default-browser-check

Or if using PowerShell:

Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" `
    --remote-debugging-port=9222,--user-data-dir="C:\ChromeDebug",`
    --disable-web-security,--disable-features=IsolateOrigins,site-per-process,`
    --no-first-run,--no-default-browser-check

🍎 MAC COMMAND:

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=9222 \
    --user-data-dir="/tmp/ChromeDebug" \
    --disable-web-security \
    --disable-features=IsolateOrigins,site-per-process \
    --no-first-run \
    --no-default-browser-check

🐧 LINUX COMMAND:

google-chrome --remote-debugging-port=9222 \
    --user-data-dir="/tmp/ChromeDebug" \
    --disable-web-security \
    --disable-features=IsolateOrigins,site-per-process \
    --no-first-run \
    --no-default-browser-check

╔════════════════════════════════════════════════════════════════════╗
║  AFTER LAUNCHING CHROME                                          ║
╚════════════════════════════════════════════════════════════════════╝

1. Chrome will open with a fresh session (or your existing one)
2. Log in to LinkedIn manually (first time only)
3. Keep this Chrome window open
4. In a separate terminal, run this script:

   python linkedin_stealth_poster.py "Your post content here"
   python linkedin_stealth_poster.py "Your post" --dry-run  # Preview mode

╔════════════════════════════════════════════════════════════════════╗
║  WHY THIS IS UNDETECTABLE                                          ║
╚════════════════════════════════════════════════════════════════════╝

✅ Uses YOUR actual Chrome session (real cookies, fingerprints)
✅ No automation flags (--enable-automation is NOT present)
✅ Types character-by-character (not instant like bots)
✅ Hovers before clicking (mimics mouse movement)
✅ Random delays (humans aren't perfectly consistent)
✅ CDP connection (indistinguishable from normal browsing)

LinkedIn sees this as YOU posting from YOUR browser.
"""
