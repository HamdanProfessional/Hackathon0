#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shared automation helper functions for social media posters.

Provides common human-like interaction utilities used across
LinkedIn, Twitter/X, and Meta (Instagram) posters.
"""

import random
import time


# ==================== CONFIGURATION ====================

# Human behavior parameters (for hover delays)
HOVER_MIN_DELAY = 0.1  # Minimum hover before click (seconds) - FAST
HOVER_MAX_DELAY = 0.3  # Maximum hover before click (seconds) - FAST

# Typing parameters
TYPING_MIN_DELAY = 0.01  # Minimum delay between keystrokes (seconds)
TYPING_MAX_DELAY = 0.03  # Maximum delay between keystrokes (seconds)
THINKING_PAUSE_PROBABILITY = 0.15  # 15% chance of a thinking pause
THINKING_PAUSE_DURATION = 0.5  # Duration of thinking pause


# ==================== HELPER FUNCTIONS ====================

def human_type(page, selector, text, description="text area"):
    """
    Type text using copy-paste (Ctrl+V) for fast posting.

    Much faster than character-by-character typing.
    Copies text to clipboard, then pastes it.

    Args:
        page: Playwright page object
        selector: CSS selector for the input field
        text: Text to type
        description: Human-readable description for logging

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"📋 Fast-pasting into {description}...")

        # Click to focus the element first
        page.click(selector, timeout=15000)
        time.sleep(random.uniform(0.2, 0.5))  # Small pause after focusing

        # Copy text to clipboard using JavaScript
        # Escape backticks and dollar signs for template literal
        escaped_text = text.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
        page.evaluate(f"navigator.clipboard.writeText(`{escaped_text}`)")
        time.sleep(0.1)

        # Paste using Ctrl+V
        page.keyboard.press("Control+V")
        time.sleep(0.3)

        print(f"✅ Finished pasting ({len(text)} chars)")
        return True

    except Exception as e:
        print(f"❌ human_type failed: {e}")
        return False


def human_type_character_by_character(page, selector, text, description="text area"):
    """
    Type text character-by-character to mimic human typing.

    Does NOT use page.type() or page.fill() which are instant.
    Instead, focuses the element and presses each key individually
    with random delays to simulate variable typing speed.

    Args:
        page: Playwright page object
        selector: CSS selector for the input field
        text: Text to type
        description: Human-readable description for logging

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"🖐️  Human-typing into: {description}")

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
        print(f"❌ human_type_character_by_character failed: {e}")
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
        print(f"🖱️  Human-clicking: {description}")

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
