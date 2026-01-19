#!/usr/bin/env node
/**
 * LinkedIn MCP Server
 *
 * Model Context Protocol server for posting to LinkedIn.
 * Uses Playwright with Chrome CDP for automation.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { chromium } from "playwright";

// Configuration
const LINKEDIN_URL = "https://www.linkedin.com/feed/";
const LINKEDIN_CREATE_POST_URL = "https://www.linkedin.com/in/hamdan-mohammad-922486374/overlay/create-post/";
const CDP_ENDPOINT = "http://127.0.0.1:9222";

// DRY_RUN mode - set via environment variable
const DRY_RUN = process.env.LINKEDIN_DRY_RUN !== "false";

// Create MCP server
const server = new Server(
  {
    name: "linkedin-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

/**
 * Post to LinkedIn using Playwright with Chrome CDP
 */
async function postToLinkedIn(content) {
  console.error(`[LinkedIn MCP] Posting to LinkedIn...`);
  console.error(`[LinkedIn MCP] Content: ${content.substring(0, 100)}...`);
  console.error(`[LinkedIn MCP] Dry Run: ${DRY_RUN}`);

  let browser = null;

  try {
    // Connect to existing Chrome CDP session
    console.error(`[LinkedIn MCP] Connecting to Chrome CDP at ${CDP_ENDPOINT}`);

    try {
      browser = await chromium.connectOverCDP(CDP_ENDPOINT);
      console.error("[LinkedIn MCP] Connected to Chrome CDP");
    } catch (error) {
      throw new Error(`Failed to connect to Chrome CDP: ${error.message}. Ensure Chrome is running with --remote-debugging-port=9222`);
    }

    const context = browser.contexts[0];
    let page;

    if (context.pages().length === 0) {
      page = await context.newPage();
    } else {
      page = context.pages()[0];
    }

    // Navigate to LinkedIn
    console.error("[LinkedIn MCP] Navigating to LinkedIn...");
    await page.goto(LINKEDIN_URL, { waitUntil: "domcontentloaded", timeout: 60000 });

    // Wait for page load
    await page.waitForTimeout(3000);

    // Check login status
    console.error("[LinkedIn MCP] Checking login status...");
    const loggedIn = await page.evaluate(() => {
      const indicators = [
        '.global-nav__me',
        '[data-control-name="identity_watcher_profile_photo"]',
        '.profile-rail-card__actor-link',
      ];
      return indicators.some(selector => document.querySelector(selector));
    });

    if (!loggedIn) {
      throw new Error("Not logged in to LinkedIn. Please log in via the Chrome automation window.");
    }

    // Navigate to create post
    console.error("[LinkedIn MCP] Opening create post overlay...");
    await page.goto(LINKEDIN_CREATE_POST_URL, { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(2000);

    // Wait for content editor
    try {
      await page.waitForSelector('div[contenteditable="true"]', { timeout: 10000 });
      console.error("[LinkedIn MCP] Create post modal loaded");
    } catch {
      console.error("[LinkedIn MCP] Warning: Modal might not be fully loaded, trying anyway...");
    }

    // Type content
    console.error("[LinkedIn MCP] Typing post content...");

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
          console.error("[LinkedIn MCP] Content typed successfully");
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
      console.error("[LinkedIn MCP] Clicking 'Post' button...");

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
            console.error("[LinkedIn MCP] Post button clicked");
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
          console.error("[LinkedIn MCP] Clicked via role/name");
        } catch {
          throw new Error("Could not find or click 'Post' button");
        }
      }

      await page.waitForTimeout(3000);
      console.error("[LinkedIn MCP] Post should be live now!");
    } else {
      console.error("[LinkedIn MCP] DRY RUN MODE - Skipping Post click");
    }

    // Close browser connection
    await browser.close();
    console.error("[LinkedIn MCP] Browser closed");

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

    console.error(`[LinkedIn MCP] Error: ${error.message}`);

    return {
      success: false,
      message: error.message,
      platform: "LinkedIn",
      error: error.message
    };
  }
}

/**
 * List available tools
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "post_to_linkedin",
        description: "Post a message to LinkedIn. Use this to publish content after approval. " +
          "Requires Chrome automation window to be logged in to LinkedIn. " +
          "Respects LINKEDIN_DRY_RUN environment variable for testing.",
        inputSchema: {
          type: "object",
          properties: {
            content: {
              type: "string",
              description: "The post content to publish. Supports hashtags, line breaks, and emojis.",
              maxLength: 3000,
            },
          },
          required: ["content"],
        },
      },
    ],
  };
});

/**
 * Handle tool calls
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "post_to_linkedin") {
    const { content } = args;

    if (!content || typeof content !== "string") {
      throw new Error("Content is required and must be a string");
    }

    if (content.length > 3000) {
      throw new Error("Content exceeds LinkedIn's 3000 character limit");
    }

    const result = await postToLinkedIn(content);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  }

  throw new Error(`Unknown tool: ${name}`);
});

/**
 * Start the server
 */
async function main() {
  console.error("[LinkedIn MCP Server] Starting...");

  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error("[LinkedIn MCP Server] Running and waiting for requests...");
  console.error(`[LinkedIn MCP Server] Dry Run Mode: ${DRY_RUN}`);
  console.error(`[LinkedIn MCP Server] CDP Endpoint: ${CDP_ENDPOINT}`);
}

main().catch((error) => {
  console.error("[LinkedIn MCP Server] Fatal error:", error);
  process.exit(1);
});
