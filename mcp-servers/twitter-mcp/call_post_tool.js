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
const TWITTER_COMPOSE_URL = "https://x.com/compose/post";
const CDP_ENDPOINT = "http://127.0.0.1:9222";

// DRY_RUN mode
const DRY_RUN = process.env.TWITTER_DRY_RUN !== "false";

/**
 * Post to Twitter/X using Playwright with Chrome CDP
 */
async function postToTwitter(content) {
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
    if (!contexts || contexts.length === 0) {
      throw new Error('No browser contexts found. Is your main Chrome running with CDP?');
    }
    context = contexts[0];

    // Find or create X/Twitter page
    const pages = context.pages();

    // Look for existing X/Twitter page
    const twitterPage = pages.find(p => p.url().includes('twitter.com') || p.url().includes('x.com'));

    if (twitterPage) {
      console.error("[Twitter/X] Using existing X/Twitter tab");
      page = twitterPage;
      // Bring the page to front
      await page.bringToFront();
    } else if (pages.length === 0) {
      console.error("[Twitter/X] Creating new tab for Twitter/X");
      page = await context.newPage();
    } else {
      page = pages[0];
    }

    // Navigate to Twitter/X compose page
    const currentUrl = page.url();
    console.error("[Twitter/X] Current URL:", currentUrl);

    // Check if we need to navigate to compose page
    if (!currentUrl.includes('x.com/compose/post')) {
      console.error("[Twitter/X] Navigating to compose page...");
      await page.goto(TWITTER_COMPOSE_URL, { waitUntil: "domcontentloaded", timeout: 60000 });
      await page.waitForTimeout(3000);
    }

    // Verify we're on the compose page
    const newUrl = page.url();
    console.error("[Twitter/X] New URL:", newUrl);

    // Check login status
    if (newUrl.includes('/login') || newUrl.includes('i/flow/login') || newUrl.includes('i/flow/signup')) {
      console.error("[Twitter/X] Detected login page");
      throw new Error("Not logged in to Twitter/X. Please log in via the Chrome automation window.");
    }

    console.error("[Twitter/X] ✓ On compose page");

    // Wait for content editor to be available
    console.error("[Twitter/X] Looking for content editor...");
    await page.waitForTimeout(2000);

    // Type content
    console.error("[Twitter/X] Typing post content...");

    const contentSelectors = [
      'div[contenteditable="true"][data-testid="tweetTextarea_0"]',  // X.com specific
      'div[contenteditable="true"][role="textbox"]',  // Generic with role
      'div[role="textbox"]',  // By role
      '[data-testid="tweetTextarea_0"]',  // By testid
      'div[contenteditable="true"]',  // Generic contenteditable
    ];

    let typed = false;
    for (const selector of contentSelectors) {
      try {
        console.error(`[Twitter/X] Trying selector: ${selector}`);
        const element = await page.$(selector);
        if (element) {
          const isVisible = await element.isVisible();
          if (isVisible) {
            console.error(`[Twitter/X] ✓ Found visible element: ${selector}`);
            // Click to focus first
            await element.click();
            await page.waitForTimeout(500);
            // Then fill
            await page.fill(selector, content);
            typed = true;
            console.error("[Twitter/X] ✓ Content typed successfully");
            break;
          }
        }
      } catch (e) {
        console.error(`[Twitter/X] Selector ${selector} failed: ${e.message}`);
        continue;
      }
    }

    if (!typed) {
      throw new Error("Could not find content editor to type post");
    }

    await page.waitForTimeout(2000);

    // Click Post button (or skip if dry run)
    if (!DRY_RUN) {
      console.error("[Twitter/X] Clicking 'Post' button...");

      // Wait a bit longer for Twitter to enable the Post button
      await page.waitForTimeout(1000);

      const postButtonSelectors = [
        '[data-testid="tweetButtonInline"]',  // X.com specific
        '[data-testid="tweetButton"]',  // Alternative X.com selector
        'button[role="button"]:has-text("Post")',  // By role and text
        'div[role="button"] span:has-text("Post")',  // Nested structure
        'button:has-text("Post")',  // Generic button
      ];

      let posted = false;
      for (const selector of postButtonSelectors) {
        try {
          console.error(`[Twitter/X] Trying Post selector: ${selector}`);
          const element = await page.$(selector);
          if (element) {
            const isVisible = await element.isVisible();
            const isDisabled = await element.isDisabled();
            if (isVisible && !isDisabled) {
              await element.click();
              posted = true;
              console.error(`[Twitter/X] ✓ Post button clicked via: ${selector}`);
              break;
            } else {
              console.error(`[Twitter/X] Button found but visible=${isVisible}, disabled=${isDisabled}`);
            }
          }
        } catch (e) {
          console.error(`[Twitter/X] Selector ${selector} failed: ${e.message}`);
          continue;
        }
      }

      if (!posted) {
        // Try via Playwright's getByRole as last resort
        try {
          await page.getByRole('button', { name: 'Post' }).click({ timeout: 5000 });
          posted = true;
          console.error("[Twitter/X] ✓ Clicked via role/name");
        } catch {
          throw new Error("Could not find or click 'Post' button");
        }
      }

      await page.waitForTimeout(5000);
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

  const result = await postToTwitter(content);

  // Output result as JSON
  console.log(JSON.stringify(result, null, 2));

  process.exit(result.success ? 0 : 1);
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
