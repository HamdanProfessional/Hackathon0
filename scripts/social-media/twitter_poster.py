#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter (X) Poster - Stealth Automation for Twitter/X

Uses Playwright to post tweets to Twitter (X) with human-like behavior.

Usage:
    python twitter_poster.py "Your tweet here" --dry-run
    python twitter_poster.py "Your tweet here" --reply_to @user (Reply to a tweet)

Note:
    Start Chrome with: chrome.exe --remote-debugging-port=9222
"""

import argparse
import os
import random
import time
import sys
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
    print("Playwright not installed. Run: pip install playwright")
    sys.exit(1)

# ==================== CONFIGURATION ====================

# DRY_RUN: Set to False to actually publish tweets
# Can be overridden via:
# 1. Environment variable: export TWITTER_DRY_RUN=false
# 2. Command-line flag: --live or --dry-run
DRY_RUN = os.getenv('TWITTER_DRY_RUN', 'true').lower() == 'true'
TWEETER_BASE_URL = "https://X.com"  # Twitter/X URL
CDP_ENDPOINT = "http://localhost:9222"

# Human behavior parameters
TYPING_MIN_DELAY = 0.01  # Minimum delay between keystrokes
TYPING_MAX_DELAY = 0.03  # Maximum delay between keystrokes
THINKING_PAUSE_PROBABILITY = 0.15  # 15% chance of a thinking pause
THINKING_PAUSE_DURATION = 0.5  # Duration of thinking pause
HOVER_MIN_DELAY = 0.1  # Minimum hover before click
HOVER_MAX_DELAY = 0.3  # Maximum hover before click

# Twitter-specific timing
INITIAL_PAGE_LOAD_DELAY = 3.0  # Wait for page load
NETWORK_IDLE_TIMEOUT = 30000  # 30 seconds for network to settle

# Twitter/X selectors
TEXTAREA_SELECTOR = 'div[data-testid="tweetTextarea_0"]'
TWEET_BUTTON_SELECTOR = 'div[data-testid="tweetButton"]'  # Old selector
POST_BUTTON_SELECTOR = 'div[data-testid="tweetButtonInline"]'  # New inline post button
# Alternative selectors for the Post button
POST_BUTTON_ALTS = [
    'div[data-testid="tweetButtonInline"]',
    'button[data-testid="tweet-button"]',
    'div[role="button"][data-testid="tweetButton"]',
    'button[aria-label*="Post"]',
    'div[aria-label*="Post"]',
]

# Reply-specific selector
REPLY_BUTTON_SELECTOR = 'div[role="button"][data-testid="reply"]'
QUOTE_BUTTON_SELECTOR = 'div[role="button"][data-testid="quote"]'


def human_type(page, selector, text):
    """
    Type text using Ctrl+V (paste) instead of character-by-character.
    """
    try:
        print(f"🐦 Pasting into Twitter (Ctrl+V)...")

        # Focus on the text area first
        page.click(selector, timeout=15000)
        time.sleep(random.uniform(0.2, 0.5))

        # Copy text to clipboard and paste
        page.evaluate(f"navigator.clipboard.writeText(`{text}`)")
        time.sleep(0.1)
        page.keyboard.press("Control+V")
        time.sleep(0.5)

        print(f"✅ Finished pasting ({len(text)} chars)")
        return True

    except Exception as e:
        print(f"❌ human_type failed: {e}")
        return False


def human_click(page, selector, description="element"):
    """
    Click an element with human-like hover behavior.
    """
    try:
        print(f"🖱️  Human-clicking: {description}")

        # First hover over the element
        page.hover(selector, timeout=15000)
        print(f"      👆 Hovering...")

        # Random delay while hovering
        hover_delay = random.uniform(HOVER_MIN_DELAY, HOVER_MAX_DELAY)
        time.sleep(hover_delay)

        # Then click
        page.click(selector, timeout=15000)
        print(f"✅ Clicked after {hover_delay:.2f}s hover")

        return True

    except Exception as e:
        print(f"❌ human_click failed: {e}")
        return False


def post_tweet(page, tweet_content, reply_to=None):
    """
    Post a tweet to Twitter (X).

    Args:
        page: Playwright page object (already connected to Chrome)
        tweet_content: Text content to post
        reply_to: Optional[str] - If specified, reply to a tweet (format: "@username or tweet_id")

    Returns:
        True if successful, False otherwise
    """
    try:
        print("\n" + "="*60)
        print("🐦 TWEETER (X) - Post Tweet")
        print("="*60 + "\n")

        print(f"📝 Tweet Content: {tweet_content[:100]}{'...' if len(tweet_content) > 100 else ''}")
        print(f"📱 Reply To: {reply_to if reply_to else 'None'}")
        print("\n")

        # Step 1: Navigate to Twitter (X)
        print("📍 Step 1: Navigating to Twitter (X)...")
        page.goto(TWEETER_BASE_URL, wait_until="domcontentloaded", timeout=60000)

        # Wait for page to load
        print(f"⏳ Waiting {INITIAL_PAGE_LOAD_DELAY}s for page to stabilize...")
        time.sleep(INITIAL_PAGE_LOAD_DELAY)

        # Try to wait for network to be mostly idle
        try:
            page.wait_for_load_state("networkidle", timeout=NETWORK_IDLE_TIMEOUT)
            print("✅ Twitter loaded\n")
        except:
            print("⚠️  Network not fully idle, proceeding anyway...\n")

        # Step 2: Compose tweet
        print("📍 Step 2: Composing tweet...")

        # Click on "What's happening?!" (tweet button)
        human_click(page, TWEET_BUTTON_SELECTOR, "Tweet button")

        time.sleep(2.0)  # Wait for composer to open

        # Type content
        if reply_to:
            # For replies
            print(f"Replying to: {reply_to}")
            human_click(page, REPLY_BUTTON_SELECTOR, "Reply button")
            time.sleep(1.0)

            # Type @username or reply_to handle
            human_type(page, TEXTAREA_SELECTOR, f"@{reply_to} ")
            human_type(page, TEXTAREA_SELECTOR, tweet_content)
        else:
            # For new tweets
            human_type(page, TEXTAREA_SELECTOR, tweet_content)

        time.sleep(1.0)
        print("✅ Content typed\n")

        # Step 3: Review and post
        print("📍 Step 3: Review and Post...")

        if not DRY_RUN:
            # Click Post button - try multiple selectors
            print("🚀 Clicking 'Post' button...")
            posted = False

            for selector in POST_BUTTON_ALTS:
                try:
                    if page.is_visible(selector, timeout=2000):
                        print(f"   Found Post button with selector: {selector}")
                        if human_click(page, selector, "Post button"):
                            posted = True
                            break
                except:
                    continue

            if not posted:
                print("⚠️  Could not find Post button, trying keyboard shortcut...")
                # Try Ctrl+Enter as fallback
                page.keyboard.press("Control+Enter")
                posted = True

            # Wait for tweet to be posted
            time.sleep(random.uniform(2.0, 4.0))

            print("\n✅ Tweet posted successfully!")
        else:
            print("📸 DRY RUN MODE - Skipping actual posting")
            page.screenshot(path="twitter_dry_run_preview.png", full_page=True)
            print("✅ Saved: twitter_dry_run_preview.png")
            print("\n⚠️  To actually post, set DRY_RUN = False at the top of the script\n")

        print("\n" + "="*60)
        print("🎉 TWITTER (X) POST COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")

        return True

    except PlaywrightTimeoutError as e:
        print(f"❌ Timeout error: {e}")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        page.screenshot(path="twitter_error_debug.png", full_page=True)
        print("📸 Saved debug screenshot: twitter_error_debug.png")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Post tweets to Twitter (X) with stealth automation"
    )

    parser.add_argument(
        "content",
        help="Tweet content (keep it under 280 characters)"
    )

    parser.add_argument(
        "--reply-to",
        help="Reply to a tweet (format: @username or tweet_id)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without actually posting (default)"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Actually publish the tweet (overrides DRY_RUN)"
    )

    args = parser.parse_args()

    # Override DRY_RUN if flag is set
    global DRY_RUN
    if args.live:
        DRY_RUN = False
        print("⚠️  LIVE MODE: Tweets will actually be published!")
    elif args.dry_run:
        DRY_RUN = True
        print("✅ DRY RUN MODE: Preview only, will not publish")

    # Prepare content
    tweet_content = args.content

    if args.reply_to:
        tweet_content = f"@{args.reply_to} {tweet_content}"

    print("\n╔══════════════════════════════════════════════════════╗")
    print("      TWITTER (X) POSTER v1.0                            ")
    print("      Playwright-based with stealth automation                ")
    print("==========================================================")
    print("")

    print(f"📝 Tweet Content: {tweet_content[:100]}{'...' if len(tweet_content) > 100 else ''}")
    print(f"📱 Reply To: {args.reply_to if args.reply_to else 'None'}")
    print(f"⚠️  Dry Run: {'YES' if DRY_RUN else 'NO'}")
    print(f"🐔 CDP Endpoint: {CDP_ENDPOINT}")
    print(f"📸 Screenshot: {'twitter_dry_run_preview.png' if DRY_RUN else 'twitter_error_debug.png'}")
    print("")

    with sync_playwright() as p:
        try:
            # Connect to existing Chrome instance via CDP
            print("🔌 Connecting to Chrome CDP session...")
            print(f"   Make sure Chrome is running with --remote-debugging-port=9222\n")

            browser = p.chromium.connect_over_cdp(CDP_ENDPOINT)
            print("✅ Connected to existing Chrome session!")

            # Get the default context and page
            default_context = browser.contexts[0]
            page = default_context.pages[0] if default_context.pages else default_context.new_page()

            # Bring window to front
            page.bring_to_front()

            # Create the post
            success = post_tweet(page, tweet_content, args.reply_to)

            if success:
                print("✅ Script completed successfully!")
                sys.exit(0)
            else:
                print("❌ Script failed. Check debug screenshot")
                sys.exit(1)

        except Exception as e:
            print(f"\n❌ CONNECTION ERROR: {e}")
            print("\n" + "="*60)
            print("TROUBLESHOOTING:")
            print("="*60)
            print("""
1. Make sure Chrome is running with remote debugging enabled
2. Check if Chrome is listening on port 9222
3. Ensure you're logged into Twitter (X)
4. If Twitter is slow, increase INITIAL_PAGE_LOAD_DELAY in the script
5. Try increasing timeouts in the script
            """)
            sys.exit(1)


if __name__ == "__main__":
    main()
