#!/usr/bin/env node
/**
 * Xero MCP Server
 *
 * Model Context Protocol server for Xero accounting integration.
 * Provides tools for creating invoices, managing contacts, and tracking payments.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import dotenv from "dotenv";
import { XeroClient } from "./xero-client.js";
import { tools } from "./tools.js";

// Load environment variables
dotenv.config();

// Create Xero client
const xeroClient = new XeroClient({
  clientId: process.env.XERO_CLIENT_ID || "",
  clientSecret: process.env.XERO_CLIENT_SECRET || "",
  redirectUri: process.env.XERO_REDIRECT_URI || "http://localhost:3000/callback",
  scopes: [
    "offline_access",
    "accounting.transactions",
    "accounting.reports.read",
  ],
});

// Create MCP server
const server = new Server(
  {
    name: "xero-mcp-server",
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
    // Check if Xero is authenticated
    if (!xeroClient.isAuthenticated()) {
      return {
        content: [
          {
            type: "text",
            text: "Error: Xero not authenticated. Please run the authentication flow first.",
          },
        ],
      };
    }

    // Execute the tool
    const result = await tool.handler(xeroClient, args || {});

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
    return {
      content: [
        {
          type: "text",
          text: `Error executing tool ${name}: ${errorMessage}`,
        },
      ],
      isError: true,
    };
  }
});

// Start server
async function main() {
  console.error("Xero MCP Server starting...");

  // Try to load existing token
  try {
    await xeroClient.loadToken();
    console.error("✓ Xero authenticated");
  } catch (error) {
    console.error("⚠ Xero not authenticated. Run authentication first:");
    console.error("  npm run authenticate");
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Xero MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
