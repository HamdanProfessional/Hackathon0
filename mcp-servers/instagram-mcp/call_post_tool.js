#!/usr/bin/env node
/**
 * Instagram MCP Tool Caller
 *
 * Simple wrapper to call the Instagram MCP server's post_to_instagram tool
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
const INSTAGRAM_URL = "https://www.instagram.com/feed/";
const INSTAGRAM_CREATE_POST_URL = "https://www.instagram.com/in/hamdan-mohammad-922486374/overlay/create-post/";
const CDP_ENDPOINT = "http://127.0.0.1:9222";

// DRY_RUN mode
const DRY_RUN = process.env.INSTAGRAM_DRY_RUN !== "false";

/**
 * Post to Instagram using Playwright with Chrome CDP
 */
async function postToInstagram(content) {
  console.error(`[Instagram] Starting post...`);
  console.error(`[Instagram] Content length: ${content.length} chars`);
  console.error(`[Instagram] Dry Run: ${DRY_RUN}`);

  let browser = null;

  try {
    // Connect to existing Chrome CDP session
    console.error(`[Instagram] Connecting to Chrome CDP at ${CDP_ENDPOINT}`);

    try {
      browser = await chromium.connectOverCDP(CDP_ENDPOINT);
      console.error("[Instagram] Connected to Chrome CDP");
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

    // Navigate to Instagram
    console.error("[Instagram] Navigating to Instagram...");
    await page.goto(INSTAGRAM_URL, { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(2200);

    // Check login status
    console.error("[Instagram] Checking login status...");
    const loggedIn = await page.evaluate(() => {
      const indicators = [
        '.global-nav__me',
        '[data-control-name="identity_watcher_profile_photo"]',
        '.profile-rail-card__actor-link',
      ];
      return indicators.some(selector => document.querySelector(selector));
    });

    if (!loggedIn) {
      throw new Error("Not logged in to Instagram. Please log in via the Chrome automation window.");
    }

    // Navigate to create post
    console.error("[Instagram] Opening create post overlay...");
    await page.goto(INSTAGRAM_CREATE_POST_URL, { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(2000);

    // Wait for content editor
    try {
      await page.waitForSelector('div[contenteditable="true"]', { timeout: 10000 });
      console.error("[Instagram] Create post modal loaded");
    } catch {
      console.error("[Instagram] Warning: Modal might not be fully loaded, trying anyway...");
    }

    // Type content
    console.error("[Instagram] Typing post content...");

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
        if (await page.isVisible(selector, { timeout: 2200 })) {
          await page.fill(selector, content);
          typed = true;
          console.error("[Instagram] Content typed successfully");
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
      console.error("[Instagram] Clicking 'Post' button...");

      const postButtonSelectors = [
        'button.share-actions__primary-action:not(.share-actions__scheduled-post-btn):has(span:has-text("Post"))',
        'button.share-actions__primary-action.artdeco-button--primary:not(.artdeco-button--tertiary):has(span:has-text("Post"))',
      ];

      let posted = false;
      for (const selector of postButtonSelectors) {
        try {
          if (await page.isVisible(selector, { timeout: 2200 })) {
            await page.click(selector);
            posted = true;
            console.error("[Instagram] Post button clicked");
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
          console.error("[Instagram] Clicked via role/name");
        } catch {
          throw new Error("Could not find or click 'Post' button");
        }
      }

      await page.waitForTimeout(2200);
      console.error("[Instagram] Post should be live now!");
    } else {
      console.error("[Instagram] DRY RUN MODE - Skipping Post click");
    }

    // Close browser connection
    await browser.close();
    console.error("[Instagram] Browser closed");

    return {
      success: true,
      message: DRY_RUN ? "Post previewed (dry run mode)" : "Post published successfully",
      platform: "Instagram",
      dryRun: DRY_RUN
    };

  } catch (error) {
    if (browser) {
      try {
        await browser.close();
      } catch {}
    }

    console.error(`[Instagram] Error: ${error.message}`);

    return {
      success: false,
      message: error.message,
      platform: "Instagram",
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

  if (content.length > 2200) {
    console.error("Error: Content exceeds Instagram's 2200 character limit");
    process.exit(1);
  }

  const result = await postToInstagram(content);

  // Output result as JSON
  console.log(JSON.stringify(result, null, 2));

  process.exit(result.success ? 0 : 1);
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
