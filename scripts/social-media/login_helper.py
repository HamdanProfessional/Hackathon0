#!/usr/bin/env python3
"""
Social Media Login Helper

Opens all three social media platforms (LinkedIn, Twitter, Meta) for login.
Run this after starting Chrome with CDP enabled.

Usage:
    1. Start Chrome with: chrome.exe --remote-debugging-port=9222
    2. Run this script: python login_helper.py
    3. Log in to all platforms (you have 10 minutes)
"""

import subprocess
import sys
import time
from pathlib import Path

# Colors for terminal output
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

def print_banner():
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{GREEN}🔐 SOCIAL MEDIA LOGIN HELPER{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def check_chrome_cdp():
    """Check if Chrome is running with CDP on port 9222."""
    try:
        import urllib.request
        import json

        response = urllib.request.urlopen("http://localhost:9222/json/version", timeout=2)
        data = json.loads(response.read())
        browser = data.get("Browser", "Unknown")
        print(f"{GREEN}✅ Chrome CDP detected!{RESET}")
        print(f"   Browser: {browser}")
        print(f"   Endpoint: http://localhost:9222\n")
        return True
    except:
        print(f"{RED}❌ Chrome CDP not detected!{RESET}")
        print(f"\n{YELLOW}⚠️  PLEASE START CHROME WITH CDP FIRST:{RESET}\n")
        print(f"   Windows: chrome.exe --remote-debugging-port=9222")
        print(f"   Or use start_chrome_cdp.bat\n")
        return False

def run_platform(name, script_path, url):
    """Run a platform's poster script for login."""
    print(f"{BLUE}{'─'*70}{RESET}")
    print(f"{GREEN}🌐 Opening {name}...{RESET}")
    print(f"{BLUE}{'─'*70}{RESET}\n")

    try:
        # Run the poster script with minimal post content
        # The script will open the platform and wait for login
        result = subprocess.run(
            [sys.executable, str(script_path), "Login test post", "--dry-run"],
            capture_output=False,
            timeout=180  # 3 minutes per platform
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"{YELLOW}⏱️  {name} timed out (this is OK if you logged in){RESET}")
        return True
    except Exception as e:
        print(f"{RED}❌ Error running {name}: {e}{RESET}")
        return False

def main():
    print_banner()

    # Check Chrome CDP
    if not check_chrome_cdp():
        print(f"{YELLOW}💡 Press Enter to try again, or Ctrl+C to exit...{RESET}")
        input()
        if not check_chrome_cdp():
            print(f"{RED}❌ Still no CDP detected. Exiting.{RESET}")
            sys.exit(1)

    print(f"{GREEN}✅ Ready to open platforms!{RESET}\n")

    # Platform scripts
    platforms = [
        ("LinkedIn", Path("scripts/social-media/linkedin_poster.py")),
        ("Twitter/X", Path("scripts/social-media/twitter_poster.py")),
        ("Meta (Facebook/Instagram)", Path("scripts/social-media/meta_poster.py")),
    ]

    print(f"{YELLOW}⏱️  You will have ~10 minutes to log in to all platforms.{RESET}")
    print(f"{YELLOW}📝 Each script will open the platform and wait for login.{RESET}\n")

    # Run each platform
    results = {}
    for name, script in platforms:
        if not script.exists():
            print(f"{RED}❌ Script not found: {script}{RESET}\n")
            results[name] = False
            continue

        success = run_platform(name, script, "")
        results[name] = success

        time.sleep(2)  # Brief pause between platforms

    # Summary
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{GREEN}📊 LOGIN SUMMARY{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

    for name, success in results.items():
        status = f"{GREEN}✅ Opened{RESET}" if success else f"{RED}❌ Failed{RESET}"
        print(f"{status} {name}")

    print(f"\n{GREEN}✅ All done! You should now be logged in to all platforms.{RESET}")
    print(f"{YELLOW}💡 Your logins will persist in Chrome for future runs.{RESET}\n")

if __name__ == "__main__":
    main()
