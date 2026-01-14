#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meta Business Suite Poster - Instagram Automation (Facebook DISABLED)

⚠️  FACEBOOK POSTING HAS BEEN DISABLED ⚠️
This script now ONLY posts to Instagram via Meta Business Suite.

Uses Meta Business Suite to post to Instagram.
Connects to your existing Chrome session via CDP to avoid bot detection.

Usage:
    python meta_poster.py "Your post content here"

Note:
    Start Chrome with: chrome.exe --remote-debugging-port=9222
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
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    print("Playwright not installed. Run: pip install playwright")
    sys.exit(1)


# ==================== CONFIGURATION ====================

# DRY_RUN: Set to False to actually publish posts
# Can be overridden via:
# 1. Environment variable: export META_DRY_RUN=false
# 2. Command-line flag: --live or --dry-run
DRY_RUN = os.getenv('META_DRY_RUN', 'true').lower() == 'true'

META_BUSINESS_SUITE_URL = "https://business.facebook.com/latest/composer"
CDP_ENDPOINT = "http://localhost:9222"

# Human behavior parameters
TYPING_MIN_DELAY = 0.01  # Minimum delay between keystrokes (seconds)
TYPING_MAX_DELAY = 0.03  # Maximum delay between keystrokes (seconds)
THINKING_PAUSE_PROBABILITY = 0.15  # 15% chance of a thinking pause
THINKING_PAUSE_DURATION = 0.5  # Duration of thinking pause

HOVER_MIN_DELAY = 0.1  # Minimum hover before click (seconds)
HOVER_MAX_DELAY = 0.3  # Maximum hover before click (seconds)

# Page load delays (Meta Business Suite is heavy)
INITIAL_PAGE_LOAD_DELAY = 5.0  # Wait after navigation
NETWORK_IDLE_TIMEOUT = 60000  # 60 seconds for network to settle


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
        page.click(selector, timeout=15000)
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


def human_click(page, selector, description="element"):
    """
    Click an element with human-like hover behavior.

    Does NOT click immediately. First hovers over the element
    (like a human moving their mouse), then waits a random duration,
    then clicks.

    Args:
        page: Playwright page object
        selector: CSS selector for the element
        description: Human-readable description for logging

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"🖱️  Human-clicking: {description} ({selector})")

        # First hover over the element (like moving mouse there)
        page.hover(selector, timeout=15000)
        print(f"      👆 Hovering...")

        # Random delay while hovering (like human hesitation)
        hover_delay = random.uniform(HOVER_MIN_DELAY, HOVER_MAX_DELAY)
        time.sleep(hover_delay)

        # Then click
        page.click(selector, timeout=15000, force=True)
        print(f"✅ Clicked after {hover_delay:.2f}s hover")

        return True

    except Exception as e:
        print(f"❌ human_click failed: {e}")
        return False


# ==================== MAIN POSTING LOGIC ====================

def select_platforms(page):
    """
    Check the Facebook and Instagram checkboxes in Business Suite.

    Args:
        page: Playwright page object

    Returns:
        Tuple of (facebook_selected, instagram_selected)
    """
    print("\n" + "-"*60)
    print("📍 Step 2: Selecting Platforms")
    print("-"*60)
    print("⚠️  Facebook posting DISABLED - Only Instagram will be selected\n")

    facebook_selected = False  # Always False - Facebook disabled
    instagram_selected = False

    # ⚠️ FACEBOOK SECTION DISABLED ⚠️
    # Facebook checkbox selection has been disabled
    # # Try multiple selectors for Facebook checkbox
    # facebook_selectors = [
    #     'input[type="checkbox"][value="facebook"]',
    #     'input[aria-label*="Facebook"]',
    #     'div[role="checkbox"][aria-label*="Facebook"]',
    #     'span:has-text("Facebook")',
    #     'label:has-text("Facebook") input[type="checkbox"]'
    # ]
    #
    # for selector in facebook_selectors:
    #     try:
    #         if page.is_visible(selector, timeout=5000):
    #             if not page.is_checked(selector):
    #                 human_click(page, selector, "Facebook checkbox")
    #             facebook_selected = True
    #             print("✅ Facebook selected")
    #             break
    #     except:
    #         continue
    #
    # if not facebook_selected:
    #     print("⚠️  Could not find Facebook checkbox (may be selected by default)")

    # Try multiple selectors for Instagram checkbox
    instagram_selectors = [
        'input[type="checkbox"][value="instagram"]',
        'input[aria-label*="Instagram"]',
        'div[role="checkbox"][aria-label*="Instagram"]',
        'span:has-text("Instagram")',
        'label:has-text("Instagram") input[type="checkbox"]'
    ]

    for selector in instagram_selectors:
        try:
            if page.is_visible(selector, timeout=5000):
                if not page.is_checked(selector):
                    human_click(page, selector, "Instagram checkbox")
                instagram_selected = True
                print("✅ Instagram selected")
                break
        except:
            continue

    if not instagram_selected:
        print("⚠️  WARNING: Instagram checkbox not found")
        print("   Your page may not have Instagram connected")
        print("   Please ensure your Instagram business account is connected\n")

    return facebook_selected, instagram_selected


def create_meta_post(page, post_content, include_facebook=True, include_instagram=True):
    """
    Create a post to Facebook and Instagram via Meta Business Suite.

    Args:
        page: Playwright page object (already connected to Chrome)
        post_content: Text content to post
        include_facebook: Whether to post to Facebook
        include_instagram: Whether to post to Instagram

    Returns:
        True if successful, False otherwise
    """
    print("\n" + "="*60)
    print("🚀 STARTING META BUSINESS SUITE POST")
    print("="*60 + "\n")

    print(f"📝 Post Content: {post_content[:100]}{'...' if len(post_content) > 100 else ''}")
    print(f"📘 Facebook: {'✅' if include_facebook else '❌'}")
    print(f"📸 Instagram: {'✅' if include_instagram else '❌'}\n")

    try:
        # Step 1: Navigate to Meta Business Suite composer
        print(f"📍 Step 1: Navigating to Meta Business Suite...")
        print(f"   URL: {META_BUSINESS_SUITE_URL}")
        print(f"   ⏳ Loading... (this is a heavy page)")

        page.goto(META_BUSINESS_SUITE_URL, wait_until="domcontentloaded", timeout=60000)

        # Meta Business Suite is VERY heavy - need generous wait
        print(f"   ⏳ Waiting {INITIAL_PAGE_LOAD_DELAY}s for page to stabilize...")
        time.sleep(INITIAL_PAGE_LOAD_DELAY)

        # Wait for network to be mostly idle
        try:
            page.wait_for_load_state("networkidle", timeout=NETWORK_IDLE_TIMEOUT)
        except:
            print("   ⚠️  Network did not fully idle, proceeding anyway...")

        print("✅ Page loaded\n")

        # Step 2: Select platforms (Facebook & Instagram)
        fb_selected, insta_selected = select_platforms(page)

        if include_facebook and not fb_selected:
            print("❌ Failed to select Facebook")
            return False

        if include_instagram and not insta_selected:
            print("⚠️  Continuing with Facebook only (Instagram not available)")

        time.sleep(random.uniform(1.0, 2.0))

        # Step 3: Click on the text area and type content
        print(f"\n📍 Step 3: Typing post content...")

        # Meta Business Suite uses multiple possible selectors for the text area
        text_area_selectors = [
            'div[contenteditable="true"][role="textbox"]',
            'div[role="textbox"]',
            'textarea',
            '[data-testid="status-attachment-mentions-input"]',
            '.notranslate',
            '[contenteditable="true"]'
        ]

        typed = False
        for selector in text_area_selectors:
            try:
                # Try to find and click on the text area
                if page.is_visible(selector, timeout=5000):
                    print(f"   Found text area with: {selector}")
                    if human_type(page, selector, post_content):
                        typed = True
                        break
            except:
                continue

        if not typed:
            print("❌ Could not find or type in the text area")
            page.screenshot(path="error_debug.png", full_page=True)
            print("📸 Saved debug screenshot: error_debug.png")
            return False

        time.sleep(random.uniform(1.5, 3.0))  # Wait for UI to update
        print("✅ Content typed\n")

        # Step 4: Wait for "Publish" button to become active
        print(f"📍 Step 4: Waiting for 'Publish' button to become active...")

        # The Publish button starts disabled and becomes enabled after typing
        publish_button_selectors = [
            'button[aria-label="Publish"]',
            'button:has-text("Publish")',
            'div[aria-label="Publish"][role="button"]',
            '[data-testid="composer-submit"]',
            'button[type="submit"]'
        ]

        publish_button = None
        for selector in publish_button_selectors:
            try:
                if page.is_visible(selector, timeout=10000):
                    # Check if button is enabled (not disabled attribute)
                    if not page.is_disabled(selector):
                        publish_button = selector
                        print(f"   Found: {selector}")
                        break
                    else:
                        print(f"   Found but disabled: {selector}")
            except:
                continue

        if not publish_button:
            print("❌ Could not find enabled 'Publish' button")
            page.screenshot(path="error_debug.png", full_page=True)
            print("📸 Saved debug screenshot: error_debug.png")
            return False

        print("✅ Publish button is ready\n")

        # Step 5: Click Publish (or skip if dry run)
        if not DRY_RUN:
            print(f"📍 Step 5: Clicking 'Publish' button...")
            time.sleep(random.uniform(1.0, 2.0))  # Final pause before posting

            if human_click(page, publish_button, "Publish button"):
                print("✅ Publish button clicked")

                # Wait for confirmation
                time.sleep(random.uniform(3.0, 5.0))
                print("\n✅ Post should be live on Facebook/Instagram now!")
            else:
                print("❌ Failed to click Publish button")
                return False
        else:
            print(f"📍 Step 5: DRY RUN MODE - Skipping Publish click")
            print("📸 Saving preview screenshot...")
            page.screenshot(path="dry_run_preview.png", full_page=True)
            print("✅ Saved: dry_run_preview.png")
            print("\n⚠️  To actually post, set DRY_RUN = False at the top of the script\n")

        print("\n" + "="*60)
        print("🎉 META POST COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")

        return True

    except PlaywrightTimeoutError as e:
        print(f"❌ Timeout error: {e}")
        print("   Meta Business Suite is slow - try increasing INITIAL_PAGE_LOAD_DELAY")
        page.screenshot(path="error_debug.png", full_page=True)
        print("📸 Saved debug screenshot: error_debug.png")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        page.screenshot(path="error_debug.png", full_page=True)
        print("📸 Saved debug screenshot: error_debug.png")
        return False


def main():
    """Main entry point for the script."""

    parser = argparse.ArgumentParser(
        description="Meta Business Suite Poster - Instagram automation (Facebook disabled)"
    )
    parser.add_argument(
        "content",
        help="Post content (wrap in quotes if it contains spaces)"
    )
    # ⚠️ FACEBOOK-ONLY OPTION DISABLED ⚠️
    # parser.add_argument(
    #     "--facebook-only",
    #     action="store_true",
    #     help="Post to Facebook only (skip Instagram) - DISABLED"
    # )
    parser.add_argument(
        "--instagram-only",
        action="store_true",
        default=True,  # Always True now since Facebook is disabled
        help=argparse.SUPPRESS  # Hide from help since it's always on
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without actually posting (default)"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Actually publish the post (overrides DRY_RUN)"
    )

    args = parser.parse_args()

    # Override DRY_RUN if flag is set
    global DRY_RUN
    if args.live:
        DRY_RUN = False
        print("⚠️  LIVE MODE: Posts will actually be published!")
    elif args.dry_run:
        DRY_RUN = True
        print("✅ DRY RUN MODE: Preview only, will not publish")

    # ⚠️ FACEBOOK DISABLED - ALWAYS INSTAGRAM ONLY ⚠️
    include_facebook = False  # Always False now
    include_instagram = True   # Always True now

    print("=" * 60)
    print("META BUSINESS SUITE POSTER v2.0")
    print("⚠️  Facebook DISABLED - Instagram ONLY")
    print("=" * 60)

    print(f"Post Content: {args.content[:100]}{'...' if len(args.content) > 100 else ''}")
    print(f"CDP Endpoint: {CDP_ENDPOINT}")
    print(f"Dry Run: {'YES' if DRY_RUN else 'NO'}")
    print(f"Instagram: {'YES' if include_instagram else 'NO'}")
    print(f"Facebook: {'DISABLED'}\n")

    with sync_playwright() as p:
        try:
            # Connect to existing Chrome instance via CDP
            print("Connecting to Chrome CDP session...")
            print(f"   Make sure Chrome is running with --remote-debugging-port=9222\n")

            browser = p.chromium.connect_over_cdp(CDP_ENDPOINT)
            print("Connected to existing Chrome session!")

            # Get the default context and page (or create new page)
            default_context = browser.contexts[0]
            page = default_context.pages[0] if default_context.pages else default_context.new_page()

            # Bring window to front
            page.bring_to_front()

            # Create the post
            success = create_meta_post(
                page,
                args.content,
                include_facebook=include_facebook,
                include_instagram=include_instagram
            )

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

4. Log in to Meta Business Suite manually in the Chrome session:
   - Go to: https://business.facebook.com
   - Make sure your Facebook Page and Instagram account are connected

5. Meta Business Suite is heavy - if it times out, increase:
   - INITIAL_PAGE_LOAD_DELAY (currently 5.0 seconds)
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
║  FIRST-TIME SETUP                                                 ║
╚════════════════════════════════════════════════════════════════════╝

1. Launch Chrome with the debugging command above

2. Log in to Meta Business Suite:
   - Go to: https://business.facebook.com
   - Navigate to Business Suite

3. Connect your Instagram account (if not already):
   - Click Settings (gear icon)
   - Add your Instagram business account
   - Verify it appears in the composer

4. Keep this Chrome window open

5. In a separate terminal, run this script:

   # Test preview mode (no posting)
   python meta_poster.py "Excited to share our latest news!" --dry-run

   # Post to Instagram (Facebook is disabled)
   python meta_poster.py "Excited to share our latest news! #growth" --live

╔════════════════════════════════════════════════════════════════════╗
║  WHY THIS IS UNDETECTABLE                                          ║
╚════════════════════════════════════════════════════════════════════╝

✅ Uses YOUR actual Chrome session (real cookies, fingerprints)
✅ No automation flags (--enable-automation is NOT present)
✅ Types character-by-character (not instant like bots)
✅ Hovers before clicking (mimics mouse movement)
✅ Random delays (humans aren't perfectly consistent)
✅ CDP connection (indistinguishable from normal browsing)
✅ Uses official Meta Business Suite (not private API)

Meta sees this as YOU posting from YOUR browser.

⚠️  NOTE: Facebook posting has been DISABLED in this version.
    Only Instagram posting is supported.
"""
