#!/usr/bin/env node
/**
 * Facebook MCP Server
 *
 * Model Context Protocol server for posting to Facebook.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { chromium } from "playwright";

// Configuration
const FACEBOOK_URL = "https://www.facebook.com";
const CDP_ENDPOINT = "http://127.0.0.1:9222";
const DRY_RUN = process.env.FACEBOOK_DRY_RUN !== "false";

// Create MCP server
const server = new Server(
  {
    name: "facebook-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

/**
 * Post to Facebook using Playwright with Chrome CDP
 */
async function postToFacebook(content) {
  console.error(`[Facebook MCP] Posting to Facebook...`);
  console.error(`[Facebook MCP] Content: ${content.substring(0, 100)}...`);
  console.error(`[Facebook MCP] Dry Run: ${DRY_RUN}`);

  let browser = null;

  try {
    browser = await chromium.connectOverCDP(CDP_ENDPOINT);
    console.error("[Facebook MCP] Connected to Chrome CDP");

    const context = browser.contexts[0];
    const page = context.pages().length > 0 ? context.pages()[0] : await context.newPage();

    // Navigate to Facebook
    console.error("[Facebook MCP] Navigating to Facebook...");
    await page.goto(FACEBOOK_URL, { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(3000);

    // Find composer box
    const selectors = [
      '[role="textbox"]',
      '[contenteditable="true"]',
      'div[contenteditable="true"]'
    ];

    let typed = false;
    for (const selector of selectors) {
      try {
        if (await page.isVisible(selector, { timeout: 5000 })) {
          // Set content and trigger blur event
          await page.evaluate((sel, text) => {
            const el = document.querySelector(sel);
            if (el) {
              el.textContent = text;
              el.dispatchEvent(new Event('blur', { bubbles: true }));
            }
          }, selector, content);
          typed = true;
          console.error("[Facebook MCP] Content typed");
          break;
        }
      } catch {}
    }

    if (!typed) {
      throw new Error("Could not find Facebook composer box");
    }

    await page.waitForTimeout(1000);

    if (!DRY_RUN) {
      // Click post button
      try {
        await page.click('button[aria-label*="Post"], button[role="button"]:has-text("Post")');
        console.error("[Facebook MCP] Post button clicked");
        await page.waitForTimeout(3000);
      } catch {
        throw new Error("Could not find Post button");
      }
    } else {
      console.error("[Facebook MCP] DRY RUN MODE - Skipping post");
    }

    await browser.close();

    return {
      success: true,
      message: DRY_RUN ? "Post previewed (dry run)" : "Post published successfully",
      platform: "Facebook",
      dryRun: DRY_RUN
    };

  } catch (error) {
    if (browser) await browser.close();
    console.error(`[Facebook MCP] Error: ${error.message}`);
    return {
      success: false,
      message: error.message,
      platform: "Facebook"
    };
  }
}

// List tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "post_to_facebook",
        description: "Post content to Facebook. Supports emojis and formatting.",
        inputSchema: {
          type: "object",
          properties: {
            content: {
              type: "string",
              description: "Post content (max 63206 characters)",
            },
          },
          required: ["content"],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "post_to_facebook") {
    const { content } = args;
    if (!content || typeof content !== "string") {
      throw new Error("Content is required");
    }

    const result = await postToFacebook(content);
    return {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
    };
  }

  throw new Error(`Unknown tool: ${name}`);
});

// Start server
async function main() {
  console.error("[Facebook MCP Server] Starting...");
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("[Facebook MCP Server] Running...");
  console.error(`[Facebook MCP Server] Dry Run: ${DRY_RUN}`);
}

main().catch((error) => {
  console.error("[Facebook MCP Server] Fatal error:", error);
  process.exit(1);
});
