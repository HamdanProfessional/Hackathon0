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
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Configuration
const INSTAGRAM_URL = "https://www.instagram.com/feed/";
const CDP_ENDPOINT = "http://127.0.0.1:9222";

// DRY_RUN mode
const DRY_RUN = process.env.INSTAGRAM_DRY_RUN !== "false";

/**
 * Generate Instagram image from text using Python script
 */
async function generateInstagramImage(text) {
  console.error("[Instagram] Generating professional image from text...");

  // Use absolute paths to avoid backslash issues
  const projectRoot = process.cwd();
  const tempImagePath = `${projectRoot}/mcp-servers/instagram-mcp/temp_instagram_image.jpg`;
  const contentFile = `${projectRoot}/mcp-servers/instagram-mcp/temp_content.txt`;
  const pythonScript = `${projectRoot}/mcp-servers/instagram-mcp/temp_generate_image.py`;
  const instagramPosterPath = `${projectRoot}/.claude/skills/facebook-instagram-manager/scripts`;

  try {
    // Write content to temp file
    fs.writeFileSync(contentFile, text);

    // Create a simpler Python script using os.path.normpath
    const pythonCode = `import sys
import os
sys.path.insert(0, r"${instagramPosterPath.replace(/\\/g, '\\\\')}")
from instagram_poster import generate_instagram_image

content = open(r"${contentFile.replace(/\\/g, '\\\\')}", "r").read()
result = generate_instagram_image(content, r"${tempImagePath.replace(/\\/g, '\\\\')}")
print(f"Generated: {result}")
`;

    fs.writeFileSync(pythonScript, pythonCode);

    // Run the Python script
    const { stdout, stderr } = await execAsync(`python "${pythonScript}"`, {
      cwd: projectRoot,
      timeout: 30000
    });

    console.error("[Instagram] Python output:", stdout || stderr);

    // Clean up temp files
    try {
      fs.unlinkSync(pythonScript);
      fs.unlinkSync(contentFile);
    } catch (e) {
      // Ignore cleanup errors
    }

    if (fs.existsSync(tempImagePath)) {
      console.error("[Instagram] ✓ Image generated successfully");
      return tempImagePath;
    } else {
      console.error("[Instagram] ⚠️ Image generation failed, continuing without image");
      return null;
    }
  } catch (error) {
    console.error(`[Instagram] Image generation error: ${error.message}`);
    return null;
  }
}

/**
 * Post to Instagram using Playwright with Chrome CDP
 */
async function postToInstagram(content) {
  console.error(`[Instagram] Starting post...`);
  console.error(`[Instagram] Content length: ${content.length} chars`);
  console.error(`[Instagram] Dry Run: ${DRY_RUN}`);

  // Generate image from text (Instagram requires an image)
  const imagePath = await generateInstagramImage(content);

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
    if (!contexts || contexts.length === 0) {
      throw new Error('No browser contexts found. Is your main Chrome running with CDP?');
    }
    context = contexts[0];

    // Find or create Instagram page
    const pages = context.pages();

    // Look for existing Instagram page
    const instagramPage = pages.find(p => p.url().includes('instagram.com'));

    if (instagramPage) {
      console.error("[Instagram] Using existing Instagram tab");
      page = instagramPage;
      // Bring the page to front
      await page.bringToFront();
    } else if (pages.length === 0) {
      console.error("[Instagram] Creating new tab for Instagram");
      page = await context.newPage();
    } else {
      page = pages[0];
    }

    // Refresh the page to ensure clean state for new post
    console.error("[Instagram] Refreshing page for clean state...");
    await page.goto('https://www.instagram.com/', { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(3000);

    // Check login status - simplified: if we're on Instagram and not on login page, we're good
    console.error("[Instagram] Checking current location...");
    const currentUrl = page.url();
    console.error("[Instagram] Current URL:", currentUrl);

    // If we're on the login page, user needs to log in
    if (currentUrl.includes('/login') || currentUrl.includes('accounts/login')) {
      console.error("[Instagram] Detected login page, URL:", currentUrl);
      throw new Error("Not logged in to Instagram. Please log in via the Chrome automation window.");
    }

    // Verify we're now on Instagram
    const newUrl = page.url();
    if (newUrl.includes('instagram.com') && !newUrl.includes('/login')) {
      console.error("[Instagram] ✓ Logged in detected (on Instagram page)");
    } else {
      throw new Error("Not logged in to Instagram. Please log in via the Chrome automation window.");
    }

    // Navigate to create post - click on the "New post" button
    console.error("[Instagram] Looking for 'New post' button...");
    await page.waitForTimeout(2000);

    // First, click the "New post" button if it exists (Instagram requires this)
    try {
      const newPostButton = await page.$('[aria-label="New post"], svg[aria-label="New post"]');
      if (newPostButton) {
        console.error("[Instagram] Clicking 'New post' button...");
        await newPostButton.click();
        await page.waitForTimeout(3000);
      }
    } catch {
      console.error("[Instagram] 'New post' button not found, might already be open...");
    }

    // Wait for the Instagram post modal to fully load
    console.error("[Instagram] Waiting for post modal to load...");
    await page.waitForTimeout(5000); // Give Instagram more time to load the modal

    // Instagram requires: Select Image → Crop → Caption → Share
    // Step 1: Check if we need to upload/select an image
    console.error("[Instagram] Checking for image upload step...");

    const uploadScreenSelectors = [
      'button:has-text("Select From Computer")',  // English
      'h3:has-text("Drag photos and videos here")',  // Drag drop area
    ];

    let needsImageUpload = false;
    for (const selector of uploadScreenSelectors) {
      try {
        if (await page.isVisible(selector, { timeout: 5000 })) {
          needsImageUpload = true;
          console.error("[Instagram] Image upload screen detected");
          break;
        }
      } catch {
        continue;
      }
    }

    if (needsImageUpload) {
      // Upload the generated image
      if (imagePath && fs.existsSync(imagePath)) {
        console.error("[Instagram] Uploading generated image:", imagePath);

        try {
          // Find the file input element
          const fileInput = await page.$('input[type="file"]');
          if (fileInput) {
            // Upload the image using setInputFiles
            await fileInput.setInputFiles(imagePath);
            console.error("[Instagram] ✓ Image uploaded successfully");
            await page.waitForTimeout(3000);

            // Click Next button after upload
            const nextButton = await page.$('div[role="button"]:has-text("Next")');
            if (nextButton) {
              console.error("[Instagram] Clicking Next (after image upload)...");
              await nextButton.click();
              await page.waitForTimeout(2000);
            }
          } else {
            console.error("[Instagram] ⚠️ Could not find file input, trying manual flow...");
          }
        } catch (uploadError) {
          console.error("[Instagram] Image upload failed:", uploadError.message);
        }
      } else {
        console.error("[Instagram] No generated image available, manual upload required");
      }
    }

    // Step 2: Look for "Next" button (crop screen) or caption area
    console.error("[Instagram] Looking for caption area or Next button...");

    const cropOrCaptionSelectors = [
      'div[role="button"]:has-text("Next")',  // Crop screen Next button
      'textarea[placeholder*="Caption"]',  // Caption textarea
      'textarea[aria-label*="Caption"]',  // Aria-label Caption
    ];

    let foundNextOrCaption = false;
    for (const selector of cropOrCaptionSelectors) {
      try {
        const element = await page.$(selector);
        if (element) {
          console.error("[Instagram] Found:", selector);
          foundNextOrCaption = true;
          // If it's a Next button (crop screen), click it
          if (selector.includes('Next') && !selector.includes('Caption')) {
            await element.click();
            console.error("[Instagram] Clicked Next (crop screen)");
            await page.waitForTimeout(2000);
          }
          break;
        }
      } catch {
        continue;
      }
    }

    // Step 3: Wait for content editor (caption area)
    try {
      await page.waitForSelector('textarea[placeholder*="Caption"], textarea[aria-label*="Caption"], div[contenteditable="true"]', { timeout: 10000 });
      console.error("[Instagram] Caption area loaded");
    } catch {
      console.error("[Instagram] Warning: Caption area not found, might need manual interaction");
    }

    // Type content (caption)
    console.error("[Instagram] Typing caption...");

    const contentSelectors = [
      'textarea[aria-label="Write a caption..."]',  // Instagram's caption textarea (exact)
      'textarea[aria-label="Caption"]',  // Aria-label exact match
      'textarea[aria-label*="caption"]',  // Aria-label contains "caption" (case insensitive)
      'textarea[placeholder*="Caption"]',  // Placeholder based
      'textarea[data-testid="post-caption-text-area"]',  // By testid
      'div[contenteditable="true"][data-lexical-text="true"]',  // Lexical editor
      'div[role="textbox"]',  // By role
      'div[contenteditable="true"]',  // Contenteditable div (fallback)
    ];

    let typed = false;
    for (const selector of contentSelectors) {
      try {
        console.error(`[Instagram] Trying caption selector: ${selector}`);
        const element = await page.$(selector);
        if (element) {
          const isVisible = await element.isVisible();
          if (isVisible) {
            console.error(`[Instagram] ✓ Found visible caption element: ${selector}`);
            // Click to focus first
            await element.click();
            await page.waitForTimeout(500);
            // Then fill
            await page.fill(selector, content);
            typed = true;
            console.error("[Instagram] ✓ Caption typed successfully");
            break;
          }
        }
      } catch (e) {
        console.error(`[Instagram] Caption selector ${selector} failed: ${e.message}`);
        continue;
      }
    }

    if (!typed) {
      throw new Error("Could not find caption editor to type post");
    }

    await page.waitForTimeout(2000);

    // Click Share button (or skip if dry run)
    if (!DRY_RUN) {
      console.error("[Instagram] Clicking 'Share' button...");

      // Wait a bit longer for Instagram to enable the Share button
      await page.waitForTimeout(1000);

      const postButtonSelectors = [
        'div[role="button"]:has-text("Share")', // Based on HTML provided
        'div.x1i10hfl:has-text("Share")',  // Alternative with specific class
        '[aria-label="Share"][role="button"]', // Aria-label based
        'button:has-text("Share")',  // Fallback
      ];

      let posted = false;
      for (const selector of postButtonSelectors) {
        try {
          console.error(`[Instagram] Trying Share selector: ${selector}`);
          const element = await page.$(selector);
          if (element) {
            const isVisible = await element.isVisible();
            const isDisabled = await element.isDisabled();
            if (isVisible && !isDisabled) {
              await element.click();
              posted = true;
              console.error(`[Instagram] ✓ Share button clicked via: ${selector}`);
              break;
            } else {
              console.error(`[Instagram] Button found but visible=${isVisible}, disabled=${isDisabled}`);
            }
          }
        } catch (e) {
          console.error(`[Instagram] Selector ${selector} failed: ${e.message}`);
          continue;
        }
      }

      if (!posted) {
        // Try via Playwright's getByRole as last resort
        try {
          await page.getByRole('button', { name: 'Share' }).click({ timeout: 5000 });
          posted = true;
          console.error("[Instagram] ✓ Clicked via role/name");
        } catch {
          throw new Error("Could not find or click 'Share' button");
        }
      }

      await page.waitForTimeout(5000);
      console.error("[Instagram] Post should be live now!");

      // Refresh page to ensure clean state for next post
      console.error("[Instagram] Refreshing page after posting...");
      await page.goto('https://www.instagram.com/', { waitUntil: "domcontentloaded", timeout: 60000 });
      await page.waitForTimeout(2000);
      console.error("[Instagram] ✓ Page refreshed for next post");
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
