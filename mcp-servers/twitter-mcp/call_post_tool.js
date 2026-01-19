#!/usr/bin/env node
/**
 * Twitter/X MCP Tool Caller
 *
 * Simple wrapper to call the Twitter/X MCP server's post_to_twitter tool
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
const TWITTER_URL = "https://www.twitter.com/feed/";
const TWITTER_CREATE_POST_URL = "https://www.twitter.com/in/hamdan-mohammad-922486374/overlay/create-post/";
const CDP_ENDPOINT = "http://127.0.0.1:9222";

// DRY_RUN mode
const DRY_RUN = process.env.TWITTER_DRY_RUN !== "false";

/**
 * Post to Twitter/X using Playwright with Chrome CDP
 */
async function postToTwitter/X(content) {
  console.error(`[Twitter/X] Starting post...`);
  console.error(`[Twitter/X] Content length: ${content.length} chars`);
  console.error(`[Twitter/X] Dry Run: ${DRY_RUN}`);

  let browser = null;

  try {
    // Connect to existing Chrome CDP session
    console.error(`[Twitter/X] Connecting to Chrome CDP at ${CDP_ENDPOINT}`);

    try {
      browser = await chromium.connectOverCDP(CDP_ENDPOINT);
      console.error("[Twitter/X] Connected to Chrome CDP");
    } catch (error) {
      throw new Error(`Failed to connect to Chrome CDP: ${error.message}. Ensure Chrome is running with --remote-debugging-port=9222`);
    }

    let context;
    let page;

    // Use the first available context from the connected browser
    // This ensures we use your existing profile
    const contexts = browser.contexts();
    if (\!contexts || contexts.length === 0) {
      throw new Error('No browser contexts found. Is your main Chrome running with CDP?');
    }
    context = contexts[0];

    // Get or create page
    const pages = context.pages();
    if (pages.length === 0) {
      page = await context.newPage();
    } else {
      page = pages[0];
    }

    // Navigate to Twitter/X
    console.error("[Twitter/X] Navigating to Twitter/X...");
    await page.goto(TWITTER_URL, { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(280);

    // Check login status
    console.error("[Twitter/X] Checking login status...");
    const loggedIn = await page.evaluate(() => {
      const indicators = [
        '.global-nav__me',
        '[data-control-name="identity_watcher_profile_photo"]',
        '.profile-rail-card__actor-link',
      ];
      return indicators.some(selector => document.querySelector(selector));
    });

    if (!loggedIn) {
      throw new Error("Not logged in to Twitter/X. Please log in via the Chrome automation window.");
    }

    // Navigate to create post
    console.error("[Twitter/X] Opening create post overlay...");
    await page.goto(TWITTER_CREATE_POST_URL, { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(2000);

    // Wait for content editor
    try {
      await page.waitForSelector('div[contenteditable="true"]', { timeout: 10000 });
      console.error("[Twitter/X] Create post modal loaded");
    } catch {
      console.error("[Twitter/X] Warning: Modal might not be fully loaded, trying anyway...");
    }

    // Type content
    console.error("[Twitter/X] Typing post content...");

    const contentSelectors = [
      'div[contenteditable="true"][role="textbox"]',
      '.ql-editor',
      '[data-artdeco-is="focused"]',
      'div[role="textbox"]',
      '[contenteditable="true"]'
    ];

    let typed = false;
    for (const selector of contentSelectors) {
      try {
        if (await page.isVisible(selector, { timeout: 280 })) {
          await page.fill(selector, content);
          typed = true;
          console.error("[Twitter/X] Content typed successfully");
          break;
        }
      } catch {
        continue;
      }
    }

    if (!typed) {
      throw new Error("Could not find content editor to type post");
    }

    await page.waitForTimeout(1000);

    // Click Post button (or skip if dry run)
    if (!DRY_RUN) {
      console.error("[Twitter/X] Clicking 'Post' button...");

      const postButtonSelectors = [
        'button.share-actions__primary-action:not(.share-actions__scheduled-post-btn):has(span:has-text("Post"))',
        'button.share-actions__primary-action.artdeco-button--primary:not(.artdeco-button--tertiary):has(span:has-text("Post"))',
      ];

      let posted = false;
      for (const selector of postButtonSelectors) {
        try {
          if (await page.isVisible(selector, { timeout: 280 })) {
            await page.click(selector);
            posted = true;
            console.error("[Twitter/X] Post button clicked");
            break;
          }
        } catch {
          continue;
        }
      }

      if (!posted) {
        // Try via role
        try {
          await page.getByRole("button", { name: "Post" }).click({ timeout: 5000 });
          posted = true;
          console.error("[Twitter/X] Clicked via role/name");
        } catch {
          throw new Error("Could not find or click 'Post' button");
        }
      }

      await page.waitForTimeout(280);
      console.error("[Twitter/X] Post should be live now!");
    } else {
      console.error("[Twitter/X] DRY RUN MODE - Skipping Post click");
    }

    // Close browser connection
    await browser.close();
    console.error("[Twitter/X] Browser closed");

    return {
      success: true,
      message: DRY_RUN ? "Post previewed (dry run mode)" : "Post published successfully",
      platform: "Twitter/X",
      dryRun: DRY_RUN
    };

  } catch (error) {
    if (browser) {
      try {
        await browser.close();
      } catch {}
    }

    console.error(`[Twitter/X] Error: ${error.message}`);

    return {
      success: false,
      message: error.message,
      platform: "Twitter/X",
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

  if (content.length > 280) {
    console.error("Error: Content exceeds Twitter/X's 280 character limit");
    process.exit(1);
  }

  const result = await postToTwitter/X(content);

  // Output result as JSON
  console.log(JSON.stringify(result, null, 2));

  process.exit(result.success ? 0 : 1);
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
