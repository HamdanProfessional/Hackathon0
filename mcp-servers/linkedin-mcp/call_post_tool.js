#!/usr/bin/env node
/**
 * LinkedIn MCP Tool Caller
 *
 * Simple wrapper to call the LinkedIn MCP server's post_to_linkedin tool
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
const LINKEDIN_URL = "https://www.linkedin.com/feed/";
const LINKEDIN_CREATE_POST_URL = "https://www.linkedin.com/in/hamdan-mohammad-922486374/overlay/create-post/";
const CDP_ENDPOINT = "http://127.0.0.1:9222";

// DRY_RUN mode
const DRY_RUN = process.env.LINKEDIN_DRY_RUN !== "false";

/**
 * Post to LinkedIn using Playwright with Chrome CDP
 */
async function postToLinkedIn(content) {
  console.error(`[LinkedIn] Starting post...`);
  console.error(`[LinkedIn] Content length: ${content.length} chars`);
  console.error(`[LinkedIn] Dry Run: ${DRY_RUN}`);

  let browser = null;

  try {
    // Connect to existing Chrome CDP session
    console.error(`[LinkedIn] Connecting to Chrome CDP at ${CDP_ENDPOINT}`);

    try {
      browser = await chromium.connectOverCDP(CDP_ENDPOINT);
      console.error("[LinkedIn] Connected to Chrome CDP");
    } catch (error) {
      throw new Error(`Failed to connect to Chrome CDP: ${error.message}. Ensure Chrome is running with --remote-debugging-port=9222`);
    }

    let context;
    let page;

    // Use the first available context from the connected browser
    // This ensures we use your existing profile
    const contexts = browser.contexts();
    if (!contexts || contexts.length === 0) {
      throw new Error("No browser contexts found. Is your main Chrome running with CDP?");
    }
    context = contexts[0];

    // Find or create LinkedIn page
    const pages = context.pages();

    // Look for existing LinkedIn page
    const linkedinPage = pages.find(p => p.url().includes('linkedin.com'));

    if (linkedinPage) {
      console.error("[LinkedIn] Using existing LinkedIn tab");
      page = linkedinPage;
      // Bring the page to front
      await page.bringToFront();
    } else if (pages.length === 0) {
      console.error("[LinkedIn] Creating new tab for LinkedIn");
      page = await context.newPage();
    } else {
      page = pages[0];
    }

    // Navigate to LinkedIn feed (only if not already on LinkedIn)
    if (!page.url().includes('linkedin.com')) {
      console.error("[LinkedIn] Navigating to LinkedIn...");
      await page.goto(LINKEDIN_URL, { waitUntil: "domcontentloaded", timeout: 60000 });
    }
    await page.waitForTimeout(2000);

    // Check login status - simplified: if we're on LinkedIn and not on login page, we're good
    console.error("[LinkedIn] Checking login status...");
    const currentUrl = page.url();

    if (currentUrl.includes('/uas/login') || currentUrl.includes('/login') || currentUrl.includes('session_redirect')) {
      console.error("[LinkedIn] Detected login page, URL:", currentUrl);
      throw new Error("Not logged in to LinkedIn. Please log in via the Chrome automation window.");
    }

    // If we're on a LinkedIn page that's not the login page, assume we're logged in
    if (currentUrl.includes('linkedin.com')) {
      console.error("[LinkedIn] ✓ Logged in detected (on LinkedIn page)");
    } else {
      throw new Error("Not on LinkedIn. Please navigate to LinkedIn in the Chrome automation window.");
    }

    // Navigate to create post
    console.error("[LinkedIn] Opening create post overlay...");
    await page.goto(LINKEDIN_CREATE_POST_URL, { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(2000);

    // Wait for content editor
    try {
      await page.waitForSelector('div[contenteditable="true"]', { timeout: 10000 });
      console.error("[LinkedIn] Create post modal loaded");
    } catch {
      console.error("[LinkedIn] Warning: Modal might not be fully loaded, trying anyway...");
    }

    // Type content
    console.error("[LinkedIn] Typing post content...");

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
        if (await page.isVisible(selector, { timeout: 3000 })) {
          await page.fill(selector, content);
          typed = true;
          console.error("[LinkedIn] Content typed successfully");
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
      console.error("[LinkedIn] Clicking 'Post' button...");

      const postButtonSelectors = [
        'button.share-actions__primary-action:not(.share-actions__scheduled-post-btn):has(span:has-text("Post"))',
        'button.share-actions__primary-action.artdeco-button--primary:not(.artdeco-button--tertiary):has(span:has-text("Post"))',
      ];

      let posted = false;
      for (const selector of postButtonSelectors) {
        try {
          if (await page.isVisible(selector, { timeout: 3000 })) {
            await page.click(selector);
            posted = true;
            console.error("[LinkedIn] Post button clicked");
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
          console.error("[LinkedIn] Clicked via role/name");
        } catch {
          throw new Error("Could not find or click 'Post' button");
        }
      }

      await page.waitForTimeout(3000);
      console.error("[LinkedIn] Post should be live now!");
    } else {
      console.error("[LinkedIn] DRY RUN MODE - Skipping Post click");
    }

    // Close browser connection
    await browser.close();
    console.error("[LinkedIn] Browser closed");

    return {
      success: true,
      message: DRY_RUN ? "Post previewed (dry run mode)" : "Post published successfully",
      platform: "LinkedIn",
      dryRun: DRY_RUN
    };

  } catch (error) {
    if (browser) {
      try {
        await browser.close();
      } catch {}
    }

    console.error(`[LinkedIn] Error: ${error.message}`);

    return {
      success: false,
      message: error.message,
      platform: "LinkedIn",
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

  if (content.length > 3000) {
    console.error("Error: Content exceeds LinkedIn's 3000 character limit");
    process.exit(1);
  }

  const result = await postToLinkedIn(content);

  // Output result as JSON
  console.log(JSON.stringify(result, null, 2));

  process.exit(result.success ? 0 : 1);
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
