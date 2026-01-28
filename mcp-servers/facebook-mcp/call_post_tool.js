#!/usr/bin/env node
/**
 * Facebook MCP Tool Caller
 *
 * Simple wrapper to call the Facebook MCP server's post_to_facebook tool
 * without needing a full MCP client implementation.
 *
 * Usage:
 *   node call_post_tool.js "Your post content here"
 */

import { chromium } from "playwright";
import fs from "fs";
import { fileURLToPath } from "url";
import { dirname } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Configuration
const FACEBOOK_URL = "https://www.facebook.com/feed/";
const CDP_ENDPOINT = "http://127.0.0.1:9222";

// DRY_RUN mode
const DRY_RUN = process.env.FACEBOOK_DRY_RUN !== "false";

/**
 * Post to Facebook using Playwright with Chrome CDP
 */
async function postToFacebook(content) {
  console.error(`[Facebook] Starting post...`);
  console.error(`[Facebook] Content length: ${content.length} chars`);
  console.error(`[Facebook] Dry Run: ${DRY_RUN}`);

  let browser = null;

  try {
    // Connect to existing Chrome CDP session
    console.error(`[Facebook] Connecting to Chrome CDP at ${CDP_ENDPOINT}`);

    try {
      browser = await chromium.connectOverCDP(CDP_ENDPOINT);
      console.error("[Facebook] Connected to Chrome CDP");
    } catch (error) {
      throw new Error(`Failed to connect to Chrome CDP: ${error.message}. Ensure Chrome is running with --remote-debugging-port=9222`);
    }

    let context;
    let page;

    // Use the first available context from the connected browser
    // This ensures we use your existing profile
    const contexts = browser.contexts();
    if (!contexts || contexts.length === 0) {
      throw new Error('No browser contexts found. Is your main Chrome running with CDP?');
    }
    context = contexts[0];

    // Find or create Facebook page
    const pages = context.pages();

    // Look for existing Facebook page
    const facebookPage = pages.find(p => p.url().includes('facebook.com'));

    if (facebookPage) {
      console.error("[Facebook] Using existing Facebook tab");
      page = facebookPage;
      // Bring the page to front
      await page.bringToFront();
    } else if (pages.length === 0) {
      console.error("[Facebook] Creating new tab for Facebook");
      page = await context.newPage();
    } else {
      page = pages[0];
    }

    // Navigate to Facebook feed (only if not already on Facebook)
    if (!page.url().includes('facebook.com')) {
      console.error("[Facebook] Navigating to Facebook...");
      await page.goto(FACEBOOK_URL, { waitUntil: "domcontentloaded", timeout: 60000 });
    }
    await page.waitForTimeout(3000);

    // Check login status - simplified: if we're on Facebook and not on login page, we're good
    console.error("[Facebook] Checking current location...");
    const currentUrl = page.url();
    console.error("[Facebook] Current URL:", currentUrl);

    // If we're on the login page, user needs to log in
    if (currentUrl.includes('/login') || currentUrl.includes('login.php')) {
      console.error("[Facebook] Detected login page, URL:", currentUrl);
      throw new Error("Not logged in to Facebook. Please log in via the Chrome automation window.");
    }

    // If we're not on Facebook, automatically navigate there
    if (!currentUrl.includes('facebook.com')) {
      console.error("[Facebook] Not on Facebook, navigating automatically...");
      await page.goto('https://www.facebook.com/feed/', { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(3000);
      console.error("[Facebook] ✓ Navigated to Facebook");
    }

    // Verify we're now on Facebook
    const newUrl = page.url();
    if (newUrl.includes('facebook.com') && !newUrl.includes('/login')) {
      console.error("[Facebook] ✓ Logged in detected (on Facebook page)");
    } else {
      throw new Error("Not logged in to Facebook. Please log in via the Chrome automation window.");
    }

    // Navigate to create post - click on the input area directly
    console.error("[Facebook] Looking for create post input...");
    await page.waitForTimeout(2000);

    // Facebook often requires clicking the composer area to activate the content editor
    console.error("[Facebook] Looking for compose button...");

    // Try clicking multiple elements to fully open the composer
    let composeClicked = false;
    try {
      // First try: Click "What's on your mind" button using Playwright's text matching
      try {
        await page.getByRole('button', { name: "What's on your mind" }).click({ timeout: 5000 });
        composeClicked = true;
        console.error("[Facebook] ✓ Clicked compose button via role/name");
      } catch {
        // Fallback to query selector
        let clicked = await page.evaluate(() => {
          const selectors = [
            '[role="button"]:has-text("What\'s on your mind")',
            '[role="button"] div:has-text("What\'s on your mind")',
            'div[role="button"] span:has-text("What\'s on your mind")',
            'span:has-text("What\'s on your mind,")',
          ];
          for (const selector of selectors) {
            const el = document.querySelector(selector);
            if (el && el.offsetParent !== null) { // Check if visible
              el.click();
              return true;
            }
          }
          return false;
        });

        if (clicked) {
          composeClicked = true;
          console.error("[Facebook] ✓ Clicked compose button via evaluate");
        }
      }
    } catch (e) {
      console.error("[Facebook] Compose button click failed:", e.message);
    }

    // Wait longer for modal to fully load
    if (composeClicked) {
      console.error("[Facebook] Waiting for modal to fully load...");
      await page.waitForTimeout(3000);
    }

    // Type content
    console.error("[Facebook] Looking for content editor...");

    const contentSelectors = [
      // Facebook-specific selectors for React composer
      'div[contenteditable="true"][data-lexical-text="true"]',  // New Facebook Lexical editor
      'div[contenteditable="true"][role="textbox"]',  // Contenteditable with textbox role
      'div[contenteditable="true"].x1urgmv5',  // Specific class for Facebook composer
      'div[contenteditable="true"]',  // Generic contenteditable
      'div[role="textbox"]',  // ARIA role
      'textarea[placeholder*="What\'s on your mind"]',  // Textarea with placeholder
      'textarea',  // Generic textarea
      'input[type="text"]',  // Generic text input
    ];

    let typed = false;
    for (const selector of contentSelectors) {
      try {
        console.error(`[Facebook] Trying selector: ${selector}`);
        // Check if element exists and is visible
        const element = await page.$(selector);
        if (element) {
          const isVisible = await element.isVisible();
          if (isVisible) {
            console.error(`[Facebook] ✓ Found visible element: ${selector}`);
            // Click to focus first (important for contenteditable)
            await element.click();
            await page.waitForTimeout(500);
            // Then fill
            await page.fill(selector, content);
            typed = true;
            console.error("[Facebook] ✓ Content typed successfully");
            break;
          }
        }
      } catch (e) {
        console.error(`[Facebook] Selector ${selector} failed: ${e.message}`);
        continue;
      }
    }

    if (!typed) {
      throw new Error("Could not find content editor to type post");
    }

    await page.waitForTimeout(2000);

    // Click Post button (or skip if dry run)
    if (!DRY_RUN) {
      console.error("[Facebook] Clicking 'Post' button...");

      // Wait a bit longer for Facebook to enable the Post button
      await page.waitForTimeout(1000);

      const postButtonSelectors = [
        '[aria-label="Post"][role="button"]', // Most reliable - Facebook uses aria-label
        'div[aria-label="Post"][role="button"]', // Sometimes wrapped in div
        'div.x1i10hfl.xjbqb8w.x1ejq31n[role="button"]', // With specific classes
        'span:has-text("Post")', // Fallback to text
      ];

      let posted = false;
      for (const selector of postButtonSelectors) {
        try {
          console.error(`[Facebook] Trying Post selector: ${selector}`);
          const element = await page.$(selector);
          if (element) {
            // Check if element is visible and enabled
            const isVisible = await element.isVisible();
            const isDisabled = await element.isDisabled();
            if (isVisible && !isDisabled) {
              await element.click();
              posted = true;
              console.error("[Facebook] ✓ Post button clicked via:", selector);
              break;
            } else {
              console.error(`[Facebook] Button found but visible=${isVisible}, disabled=${isDisabled}`);
            }
          }
        } catch (e) {
          console.error(`[Facebook] Selector ${selector} failed: ${e.message}`);
          continue;
        }
      }

      if (!posted) {
        // Try via Playwright's getByRole as last resort
        try {
          await page.getByRole("button", { name: "Post" }).click({ timeout: 5000 });
          posted = true;
          console.error("[Facebook] Clicked via role/name");
        } catch {
          throw new Error("Could not find or click 'Post' button");
        }
      }

      await page.waitForTimeout(5000);
      console.error("[Facebook] Post should be live now!");

      // Refresh page to ensure clean state for next post
      console.error("[Facebook] Refreshing page after posting...");
      await page.goto('https://www.facebook.com/feed/', { waitUntil: "domcontentloaded", timeout: 60000 });
      await page.waitForTimeout(2000);
      console.error("[Facebook] ✓ Page refreshed for next post");
    } else {
      console.error("[Facebook] DRY RUN MODE - Skipping Post click");
    }

    // Close browser connection
    await browser.close();
    console.error("[Facebook] Browser closed");

    return {
      success: true,
      message: DRY_RUN ? "Post previewed (dry run mode)" : "Post published successfully",
      platform: "Facebook",
      dryRun: DRY_RUN
    };

  } catch (error) {
    if (browser) {
      try {
        await browser.close();
      } catch {}
    }

    console.error(`[Facebook] Error: ${error.message}`);

    return {
      success: false,
      message: error.message,
      platform: "Facebook",
      error: error.message
    };
  }
}

/**
 * Main
 */
async function main() {
  const content = process.argv[2];

  if (!content) {
    console.error("Usage: node call_post_tool.js \"<post content>\"");
    process.exit(1);
  }

  if (content.length > 63206) {
    console.error("Error: Content exceeds Facebook's 63206 character limit");
    process.exit(1);
  }

  const result = await postToFacebook(content);

  // Output result as JSON
  console.log(JSON.stringify(result, null, 2));

  process.exit(result.success ? 0 : 1);
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
