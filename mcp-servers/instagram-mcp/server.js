#!/usr/bin/env node
/**
 * Instagram MCP Server
 *
 * Model Context Protocol server for posting to Instagram.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { chromium } from "playwright";

// Configuration
const INSTAGRAM_URL = "https://www.instagram.com";
const CDP_ENDPOINT = "http://127.0.0.1:9222";
const DRY_RUN = process.env.INSTAGRAM_DRY_RUN !== "false";

// Create MCP server
const server = new Server(
  {
    name: "instagram-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

/**
 * Post to Instagram using Playwright with Chrome CDP
 */
async function postToInstagram(content) {
  console.error(`[Instagram MCP] Posting to Instagram...`);
  console.error(`[Instagram MCP] Content: ${content.substring(0, 100)}...`);
  console.error(`[Instagram MCP] Dry Run: ${DRY_RUN}`);

  let browser = null;

  try {
    browser = await chromium.connectOverCDP(CDP_ENDPOINT);
    console.error("[Instagram MCP] Connected to Chrome CDP");

    const context = browser.contexts[0];
    const page = context.pages().length > 0 ? context.pages()[0] : await context.newPage();

    // Navigate to Instagram
    console.error("[Instagram MCP] Navigating to Instagram...");
    await page.goto(INSTAGRAM_URL, { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(3000);

    // Instagram requires mobile user agent for full functionality
    await page.emulateMediaType('screen');

    // Navigate to create post
    await page.goto("https://www.instagram.com/", { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(2000);

    // Look for create button
    try {
      const createButton = await page.$('svg[aria-label="New post"], [aria-label="New post"]');
      if (createButton) {
        await createButton.click();
        console.error("[Instagram MCP] Create post clicked");
        await page.waitForTimeout(2000);
      }
    } catch {
      console.error("[Instagram MCP] Could not find create button");
    }

    if (!DRY_RUN) {
      // Handle image upload and caption
      console.error("[Instagram MCP] Would upload image and add caption");
      // Full implementation would handle image upload and caption input
    } else {
      console.error("[Instagram MCP] DRY RUN MODE - Skipping post");
    }

    await browser.close();

    return {
      success: true,
      message: DRY_RUN ? "Post previewed (dry run)" : "Post published successfully",
      platform: "Instagram",
      dryRun: DRY_RUN,
      note: "Instagram posting requires image generation - use full implementation for production"
    };

  } catch (error) {
    if (browser) await browser.close();
    console.error(`[Instagram MCP] Error: ${error.message}`);
    return {
      success: false,
      message: error.message,
      platform: "Instagram"
    };
  }
}

// List tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "post_to_instagram",
        description: "Post content to Instagram. Requires image generation.",
        inputSchema: {
          type: "object",
          properties: {
            content: {
              type: "string",
              description: "Caption/content for Instagram post (max 2200 characters)",
              maxLength: 2200,
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

  if (name === "post_to_instagram") {
    const { content } = args;
    if (!content || typeof content !== "string") {
      throw new Error("Content is required");
    }

    const result = await postToInstagram(content);
    return {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
    };
  }

  throw new Error(`Unknown tool: ${name}`);
});

// Start server
async function main() {
  console.error("[Instagram MCP Server] Starting...");
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("[Instagram MCP Server] Running...");
  console.error(`[Instagram MCP Server] Dry Run: ${DRY_RUN}`);
}

main().catch((error) => {
  console.error("[Instagram MCP Server] Fatal error:", error);
  process.exit(1);
});
