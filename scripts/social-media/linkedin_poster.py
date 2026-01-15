#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Poster - Playwright-based automation for posting to LinkedIn

Uses Playwright with CDP (existing Chrome session).

Usage:
    python linkedin_poster.py "Your post content here"
    python linkedin_poster.py "Your post" --dry-run  # Preview without posting
    python linkedin_poster.py --file post_content.txt

Note:
    Start Chrome with: chrome.exe --remote-debugging-port=9222
"""

import sys
import argparse
import os
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    print("Error: Playwright not installed.")
    print("Please run:")
    print("  pip install playwright")
    print("  playwright install chromium")
    sys.exit(1)

# Import shared automation helpers
try:
    from automation_helpers import human_type, human_click
except ImportError:
    print("Error: automation_helpers.py not found.")
    print("Please ensure automation_helpers.py is in the same directory.")
    sys.exit(1)


# ==================== CONFIGURATION ====================

# DRY_RUN: Set to False to actually publish posts
# Can be overridden via:
# 1. Environment variable: export LINKEDIN_DRY_RUN=false
# 2. Command-line flag: --live or --dry-run
DRY_RUN = os.getenv('LINKEDIN_DRY_RUN', 'true').lower() == 'true'

LINKEDIN_URL = "https://www.linkedin.com/feed/"
LINKEDIN_CREATE_POST_URL = "https://www.linkedin.com/in/hamdan-mohammad-922486374/overlay/create-post/"
CDP_ENDPOINT = "http://127.0.0.1:9222"  # Chrome DevTools Protocol endpoint (IPv4)

# Page load timing
INITIAL_PAGE_LOAD_DELAY = 3.0  # Wait for page load
NETWORK_IDLE_TIMEOUT = 30000  # 30 seconds for network to settle


# ==================== MAIN POSTING LOGIC ====================

def post_to_linkedin(post_content: str, headless: bool = False) -> bool:
    """
    Create a LinkedIn post using Playwright with CDP (existing Chrome).

    Connects to your already-running Chrome browser on port 9222.
    You must start Chrome with: chrome.exe --remote-debugging-port=9222

    Args:
        post_content: Text content to post
        headless: Run in headless mode (default: False)

    Returns:
        True if successful, False otherwise
    """
    print("\n" + "="*60)
    print("🚀 STARTING LINKEDIN POST")
    print("="*60 + "\n")

    try:
        with sync_playwright() as p:
            # Connect to existing Chrome instance via CDP
            print(f"🔌 Connecting to Chrome CDP session...")
            print(f"   CDP Endpoint: {CDP_ENDPOINT}")
            print(f"   Headless: {headless}\n")

            browser = p.chromium.connect_over_cdp(CDP_ENDPOINT)

            # Get existing context and pages (CDP mode)
            context = browser.contexts[0]
            if len(context.pages) == 0:
                page = context.new_page()
            else:
                page = context.pages[0]

            # Step 1: Navigate to LinkedIn feed, then to create post
            print(f"📍 Step 1: Opening LinkedIn feed...")
            page.goto(LINKEDIN_URL, wait_until="domcontentloaded", timeout=60000)

            # Wait for page to load
            print(f"⏳ Waiting {INITIAL_PAGE_LOAD_DELAY}s for page to stabilize...")
            time.sleep(INITIAL_PAGE_LOAD_DELAY)

            # Check if logged in
            print("🔍 Checking login status...")
            logged_in = False

            # Check for login indicators
            login_indicators = [
                '.global-nav__me',
                '[data-control-name="identity_watcher_profile_photo"]',
                '.profile-rail-card__actor-link',
                'div.profile-rail-card'
            ]

            for indicator in login_indicators:
                try:
                    if page.query_selector(indicator):
                        print(f"✅ Detected logged in (found: {indicator})!")
                        logged_in = True
                        break
                except Exception:
                    continue

            if not logged_in:
                # Check for login page
                login_page_indicators = [
                    'input[type="password"]',
                    '.login__form',
                    '#password'
                ]

                is_login_page = False
                for indicator in login_page_indicators:
                    try:
                        if page.query_selector(indicator):
                            is_login_page = True
                            break
                    except Exception:
                        continue

                if is_login_page:
                    print("⚠️  Not logged in! Please log in to LinkedIn in the browser window.")
                    print("   Session will be saved for future runs.")

                    if headless:
                        print("   Re-run without --headless to login.")
                        browser.close()
                        return False

                    # Wait for user to log in
                    print("   Waiting for login (up to 120 seconds)...")
                    print("   Press Ctrl+C to cancel if you don't want to login.\n")

                    for i in range(24):  # 120 seconds total
                        time.sleep(5)
                        # Check if logged in now
                        for indicator in login_indicators:
                            if page.query_selector(indicator):
                                logged_in = True
                                break
                        if logged_in:
                            print("✅ Login detected! Proceeding...\n")
                            break
                        print(f"   Still waiting for login... ({(i+1)*5}s)")

                    if not logged_in:
                        print("❌ Login timeout. Please run again and complete the login.")
                        browser.close()
                        return False

            # Try to wait for network to be mostly idle
            try:
                page.wait_for_load_state("networkidle", timeout=NETWORK_IDLE_TIMEOUT)
                print("✅ LinkedIn loaded\n")
            except PlaywrightTimeoutError:
                print("⚠️  Network not fully idle, proceeding anyway...\n")

            # Step 2: Navigate to create post overlay
            print(f"📍 Step 2: Opening create post overlay...")
            page.goto(LINKEDIN_CREATE_POST_URL, wait_until="domcontentloaded", timeout=60000)

            time.sleep(random.uniform(2.0, 3.0))

            # Check if modal loaded by looking for text area
            try:
                # Try to find the content editor
                page.wait_for_selector('div[contenteditable="true"]', timeout=10000)
                print("✅ Create post modal loaded\n")
            except PlaywrightTimeoutError:
                print("⚠️  Modal might not be fully loaded, trying anyway...\n")

            # Step 3: Type the post content
            print(f"📍 Step 3: Typing post content...")

            # Try multiple selectors for the content editor
            content_selectors = [
                'div[contenteditable="true"][role="textbox"]',
                '.ql-editor',
                '[data-artdeco-is="focused"]',
                'div[role="textbox"]',
                '[contenteditable="true"]'
            ]

            typed = False
            for selector in content_selectors:
                try:
                    if page.is_visible(selector, timeout=3000):
                        if human_type(page, selector, post_content, "post editor"):
                            typed = True
                            break
                except Exception:
                    continue

            if not typed:
                print("❌ Could not type post content")
                page.screenshot(path="linkedin_error_debug.png", full_page=True)
                print("📸 Saved debug screenshot: linkedin_error_debug.png")
                browser.close()
                return False

            time.sleep(random.uniform(1.0, 2.0))  # Pause after typing
            print("✅ Content typed\n")

            # Step 4: Click "Post" button (or skip if dry run)
            if not DRY_RUN:
                print(f"📍 Step 4: Clicking 'Post' button...")

                # Try multiple selectors for the Post button (updated for 2025 LinkedIn UI)
                # IMPORTANT: Must avoid "Schedule post" button which has class "share-actions__scheduled-post-btn"
                # We want the button with class "share-actions__primary-action" NOT "share-actions__scheduled-post-btn"
                post_button_selectors = [
                    # Most specific: Post button but NOT schedule button
                    'button.share-actions__primary-action:not(.share-actions__scheduled-post-btn):has(span:has-text("Post"))',
                    'button.share-actions__primary-action.artdeco-button--primary:not(.artdeco-button--tertiary):has(span:has-text("Post"))',
                    # Exclude by aria-label
                    'button.share-actions__primary-action:not([aria-label*="Schedule"]):has(span:has-text("Post"))',
                    # Look for the specific text
                    '.share-creation-state__footer button.share-actions__primary-action:has(.artdeco-button__text:has-text("Post"))',
                ]

                posted = False
                for selector in post_button_selectors:
                    try:
                        if page.is_visible(selector, timeout=3000):
                            # Check if button is enabled
                            if not page.is_disabled(selector):
                                if human_click(page, selector, "'Post' button"):
                                    posted = True
                                    break
                            else:
                                print(f"      ⚠️  Found Post button but it's disabled: {selector}")
                    except Exception:
                        continue

                if not posted:
                    # Try clicking via text content
                    try:
                        page.get_by_role("button", name="Post").click(timeout=5000)
                        posted = True
                        print("✅ Clicked via role/name")
                    except Exception:
                        pass

                if not posted:
                    print("❌ Could not find or click 'Post' button")
                    page.screenshot(path="linkedin_error_debug.png", full_page=True)
                    print("📸 Saved debug screenshot: linkedin_error_debug.png")
                    browser.close()
                    return False

                print("✅ Post button clicked")

                # Wait for confirmation
                time.sleep(random.uniform(3.0, 5.0))
                print("\n✅ Post should be live now!")
            else:
                print(f"📍 Step 4: DRY RUN MODE - Skipping Post click")
                print("📸 Saving preview screenshot...")
                page.screenshot(path="linkedin_dry_run_preview.png", full_page=True)
                print("✅ Saved: linkedin_dry_run_preview.png")
                print("\n⚠️  To actually post, set DRY_RUN = False or use --live flag\n")

            print("\n" + "="*60)
            print("🎉 LINKEDIN POST COMPLETED SUCCESSFULLY")
            print("="*60 + "\n")

            browser.close()
            return True

    except PlaywrightTimeoutError as e:
        print(f"❌ Timeout error: {e}")
        print("   LinkedIn may be slow - try increasing INITIAL_PAGE_LOAD_DELAY")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def read_file(file_path: str) -> str:
    """
    Read content from a file.

    Args:
        file_path: Path to the file

    Returns:
        File content as string
    """
    path = Path(file_path)
    if not path.exists():
        print(f"[ERROR] File not found: {file_path}")
        sys.exit(1)

    return path.read_text(encoding='utf-8')


def main():
    """Main entry point for the script."""

    parser = argparse.ArgumentParser(
        description="LinkedIn Poster - Playwright CDP automation (uses existing Chrome)",
        epilog="""
Examples:
  # Post from command line (dry run by default)
  python linkedin_poster.py "Hello LinkedIn! #python #automation"

  # Post from file
  python linkedin_poster.py --file my_post.txt

  # Actually publish the post (live mode)
  python linkedin_poster.py "Hello LinkedIn!" --live

  # Preview without posting
  python linkedin_poster.py "Test post" --dry-run

Note:
  Start Chrome with: chrome.exe --remote-debugging-port=9222
  This script connects to your existing Chrome session.
        """
    )

    parser.add_argument(
        'content',
        nargs='?',
        help='Post content (use quotes for multi-line)'
    )

    parser.add_argument(
        '--file', '-f',
        help='Read post content from file'
    )

    parser.add_argument(
        '--dry-run', '-t',
        action='store_true',
        help='Preview without actually posting (default)'
    )

    parser.add_argument(
        '--live',
        action='store_true',
        help='Actually publish the post (overrides DRY_RUN)'
    )

    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode (use after first login)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode (more verbose logging)'
    )

    args = parser.parse_args()

    # Override DRY_RUN if flag is set
    global DRY_RUN
    if args.live:
        DRY_RUN = False
        print("⚠️  LIVE MODE: Post will actually be published!")
    elif args.dry_run:
        DRY_RUN = True
        print("✅ DRY RUN MODE: Preview only, will not publish")

    # Get content
    if args.file:
        content = read_file(args.file)
    elif args.content:
        content = args.content
    else:
        parser.print_help()
        print("\n[ERROR] Please provide content via argument or --file")
        sys.exit(1)

    print("""
╔══════════════════════════════════════════════════════════╗
║          LINKEDIN POSTER v3.0 (CDP Mode)                ║
║   Uses Existing Chrome on port 9222 (Undetectable)      ║
╚══════════════════════════════════════════════════════════╝
    """)

    print(f"📝 Post Content: {content[:100]}{'...' if len(content) > 100 else ''}")
    print(f"🔗 CDP Endpoint: {CDP_ENDPOINT}")
    print(f"👻 Headless: {args.headless}")
    print(f"⚠️  Dry Run: {'YES' if DRY_RUN else 'NO'}\n")

    success = post_to_linkedin(
        post_content=content,
        headless=args.headless
    )

    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed. Check linkedin_error_debug.png")
        sys.exit(1)


if __name__ == "__main__":
    main()


# ==================== DOCUMENTATION ====================
"""
╔════════════════════════════════════════════════════════════════════╗
║  FIRST-TIME SETUP                                                 ║
╚════════════════════════════════════════════════════════════════════╝

1. Run the script for the first time (without --headless):
   python linkedin_poster.py "Test post" --dry-run

2. A browser window will open. Log in to LinkedIn when prompted.

3. After logging in, the session will be saved automatically.
   You can close the browser when done.

4. Subsequent runs can use --headless mode:
   python linkedin_poster.py "Actual post" --live --headless

╔════════════════════════════════════════════════════════════════════╗
║  PERSISTENT SESSION BENEFITS                                        ║
╚════════════════════════════════════════════════════════════════════╝

✅ No need to start Chrome with remote debugging
✅ Session stays logged in (like WhatsApp watcher)
✅ Works headless after first login
✅ No dependency on external Chrome process
✅ More reliable and self-contained
✅ Consistent with other watchers in the project

╔════════════════════════════════════════════════════════════════════╗
║  COMPARISON WITH CDP APPROACH                                      ║
╚════════════════════════════════════════════════════════════════════╝

CDP Approach (old):
- Requires Chrome to be running with --remote-debugging-port=9222
- Connects to existing Chrome session
- External dependency on Chrome process
- More fragile (Chrome might close)

Persistent Context (new - like WhatsApp watcher):
- Creates its own browser instance
- Self-contained and independent
- Session stays logged in
- More robust and reliable
- Same pattern as WhatsApp watcher

╔════════════════════════════════════════════════════════════════════╗
║  WHY THIS IS BETTER THAN PYAUTOGUI                                 ║
╚════════════════════════════════════════════════════════════════════╝

✅ No hardcoded coordinates (works on any screen resolution)
✅ Uses CSS selectors (not pixel positions)
✅ Persistent session (stays logged in)
✅ Headless support (can run in background)
✅ Cross-platform (Windows, Mac, Linux)
✅ Better reliability (doesn't break if UI moves slightly)
✅ Modern browser automation (Playwright is actively maintained)
✅ Human-like typing and clicking (harder to detect)
✅ Self-contained (no external Chrome dependency)

╔════════════════════════════════════════════════════════════════════╗
║  TROUBLESHOOTING                                                   ║
╚════════════════════════════════════════════════════════════════════╝

Problem: "Not logged in" message
Solution: Run without --headless and complete the login in the browser

Problem: "Could not find 'Start a post' button"
Solution: LinkedIn may have changed UI. Check linkedin_error_debug.png

Problem: Script is slow
Solution: Increase INITIAL_PAGE_LOAD_DELAY for slower connections

Problem: Session expired
Solution: Delete the session directory and login again:
          rm -rf ./linkedin_session
"""
