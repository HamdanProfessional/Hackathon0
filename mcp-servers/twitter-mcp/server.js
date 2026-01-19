#!/usr/bin/env node
/**
 * Twitter/X MCP Server
 *
 * Model Context Protocol server for posting to Twitter (X).
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { chromium } from "playwright";

// Configuration
const TWITTER_URL = "https://twitter.com";
const CDP_ENDPOINT = "http://127.0.0.1:9222";
const DRY_RUN = process.env.TWITTER_DRY_RUN !== "false";

// Create MCP server
const server = new Server(
  {
    name: "twitter-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

/**
 * Post to Twitter using Playwright with Chrome CDP
 */
async function postToTwitter(content) {
  console.error(`[Twitter MCP] Posting to Twitter...`);
  console.error(`[Twitter MCP] Content: ${content.substring(0, 100)}...`);
  console.error(`[Twitter MCP] Dry Run: ${DRY_RUN}`);

  let browser = null;

  try {
    // Connect to Chrome CDP
    browser = await chromium.connectOverCDP(CDP_ENDPOINT);
    console.error("[Twitter MCP] Connected to Chrome CDP");

    const context = browser.contexts[0];
    const page = context.pages().length > 0 ? context.pages()[0] : await context.newPage();

    // Navigate to Twitter
    console.error("[Twitter MCP] Navigating to Twitter...");
    await page.goto("https://twitter.com/intent/tweet?text=" + encodeURIComponent(content), { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(2000);

    if (!DRY_RUN) {
      // Find and click tweet button
      const tweetButton = await page.$('div[role="button"]:has-text("Post")');
      if (tweetButton) {
        await tweetButton.click();
        console.error("[Twitter MCP] Tweet button clicked");
        await page.waitForTimeout(3000);
      }
    } else {
      console.error("[Twitter MCP] DRY RUN MODE - Skipping tweet");
    }

    await browser.close();

    return {
      success: true,
      message: DRY_RUN ? "Tweet previewed (dry run)" : "Tweet posted successfully",
      platform: "Twitter",
      dryRun: DRY_RUN
    };

  } catch (error) {
    if (browser) await browser.close();
    console.error(`[Twitter MCP] Error: ${error.message}`);
    return {
      success: false,
      message: error.message,
      platform: "Twitter"
    };
  }
}

// List tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "post_to_twitter",
        description: "Post a tweet to Twitter/X. Max 280 characters.",
        inputSchema: {
          type: "object",
          properties: {
            content: {
              type: "string",
              description: "Tweet content (max 280 characters)",
              maxLength: 280,
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

  if (name === "post_to_twitter") {
    const { content } = args;
    if (!content || typeof content !== "string") {
      throw new Error("Content is required");
    }
    if (content.length > 280) {
      throw new Error("Tweet exceeds 280 character limit");
    }

    const result = await postToTwitter(content);
    return {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
    };
  }

  throw new Error(`Unknown tool: ${name}`);
});

// Start server
async function main() {
  console.error("[Twitter MCP Server] Starting...");
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("[Twitter MCP Server] Running...");
  console.error(`[Twitter MCP Server] Dry Run: ${DRY_RUN}`);
}

main().catch((error) => {
  console.error("[Twitter MCP Server] Fatal error:", error);
  process.exit(1);
});
