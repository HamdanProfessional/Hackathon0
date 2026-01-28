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
    console.error("[Facebook] Checking login status...");
    const currentUrl = page.url();

    if (currentUrl.includes('/login') || currentUrl.includes('login.php')) {
      console.error("[Facebook] Detected login page, URL:", currentUrl);
      throw new Error("Not logged in to Facebook. Please log in via the Chrome automation window.");
    }

    // If we're on a Facebook page that's not the login page, assume we're logged in
    if (currentUrl.includes('facebook.com')) {
      console.error("[Facebook] ✓ Logged in detected (on Facebook page)");
    } else {
      throw new Error("Not on Facebook. Please navigate to Facebook in the Chrome automation window.");
    }

    // Navigate to create post - click on the input area directly
    console.error("[Facebook] Looking for create post input...");
    await page.waitForTimeout(2000);

    // Click on the "What's on your mind" input to open the composer
    try {
      const composeButton = await page.$('[role="button"]:has-text("What\'s on your mind"), [role="button"].xi81zsa');
      if (composeButton) {
        console.error("[Facebook] Clicking compose button...");
        await composeButton.click();
        await page.waitForTimeout(2000);
      }
    } catch {
      console.error("[Facebook] Could not find compose button, trying direct fill...");
    }

    // Wait for content editor
    try {
      await page.waitForSelector('[role="button"]:has-text("What\'s on your mind"), div[contenteditable="true"]', { timeout: 10000 });
      console.error("[Facebook] Create post modal loaded");
    } catch {
      console.error("[Facebook] Warning: Modal might not be fully loaded, trying anyway...");
    }

    // Type content
    console.error("[Facebook] Typing post content...");

    const contentSelectors = [
      'div[contenteditable="true"]', // Facebook's contenteditable div in composer
      '[role="textbox"]',
      '[role="button"]:has(span:has-text("What\'s on your mind"))', // Click to focus
      'span.x1lliihq:has-text("What\'s on your mind")',
    ];

    let typed = false;
    for (const selector of contentSelectors) {
      try {
        if (await page.isVisible(selector, { timeout: 63206 })) {
          await page.fill(selector, content);
          typed = true;
          console.error("[Facebook] Content typed successfully");
          break;
        }
      } catch {
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

      const postButtonSelectors = [
        '[aria-label="Post"][role="button"]', // Most reliable - Facebook uses aria-label
        'div[aria-label="Post"][role="button"]', // Sometimes wrapped in div
        'span:has-text("Post")', // Fallback to text
      ];

      let posted = false;
      for (const selector of postButtonSelectors) {
        try {
          const element = await page.$(selector);
          if (element) {
            await element.click();
            posted = true;
            console.error("[Facebook] Post button clicked via:", selector);
            break;
          }
        } catch {
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

      await page.waitForTimeout(63206);
      console.error("[Facebook] Post should be live now!");
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
