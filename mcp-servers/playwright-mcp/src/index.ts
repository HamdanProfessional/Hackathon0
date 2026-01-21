#!/usr/bin/env node
/**
 * Playwright MCP Server
 *
 * Model Context Protocol server for Playwright browser automation.
 * Provides tools for web navigation, content extraction, and browser control.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import dotenv from "dotenv";
import { BrowserManager } from "./browser.js";
import { tools } from "./tools.js";

// Load environment variables
dotenv.config();

// Create browser manager
const browserManager = new BrowserManager({
  cdpEndpoint: process.env.CDP_ENDPOINT || 'http://localhost:9222',
  headless: process.env.HEADLESS !== 'false',  // Default to headless
  useCDP: process.env.USE_CDP === 'true',  // Default to headless for cloud VM
});

// Create MCP server
const server = new Server(
  {
    name: "playwright-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: tools.map((tool) => ({
      name: tool.name,
      description: tool.description,
      inputSchema: tool.inputSchema,
    })),
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  // Find the tool
  const tool = tools.find((t) => t.name === name);
  if (!tool) {
    throw new Error(`Tool not found: ${name}`);
  }

  try {
    // Ensure browser is connected
    if (!browserManager.isConnected()) {
      await browserManager.connect();
      console.error("Playwright: Connected to Chrome CDP");
    }

    // Execute the tool
    const result = await tool.handler(browserManager, args || {});

    return {
      content: [
        {
          type: "text",
          text: result,
        },
      ],
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error(`Playwright error executing tool ${name}:`, errorMessage);

    return {
      content: [
        {
          type: "text",
          text: `Error: ${errorMessage}`,
        },
      ],
      isError: true,
    };
  }
});

// Start server
async function main() {
  console.error("Playwright MCP Server starting...");
  console.error(`CDP Endpoint: ${browserManager['config'].cdpEndpoint}`);

  // Verify Chrome CDP is available
  try {
    await browserManager.connect();
    console.error("Playwright: ✓ Connected to Chrome CDP");
    await browserManager.disconnect();
  } catch (error) {
    console.error("Playwright: ✗ Failed to connect to Chrome CDP");
    console.error("  Make sure START_AUTOMATION_CHROME.bat is running");
    console.error(`  Error: ${error}`);
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error("Playwright MCP Server running on stdio");
  console.error("Available tools:", tools.map((t) => t.name).join(", "));

  // Graceful shutdown
  process.on('SIGINT', async () => {
    console.error("\nShutting down Playwright MCP Server...");
    await browserManager.disconnect();
    process.exit(0);
  });
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});
