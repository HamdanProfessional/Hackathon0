#!/usr/bin/env node
/**
 * Email MCP Server
 *
 * Model Context Protocol server for Gmail integration.
 * Provides tools for sending emails, creating drafts, and managing communications.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import dotenv from "dotenv";
import { EmailClient } from "./email-client.js";
import { tools } from "./tools.js";

// Load environment variables
dotenv.config();

// Create email client
const emailClient = new EmailClient({
  credentialsPath: process.env.GOOGLE_CREDENTIALS_PATH || ".",
  tokenPath: process.env.GMAIL_TOKEN_PATH || ".gmail_mcp_token.json",
});

// Create MCP server
const server = new Server(
  {
    name: "email-mcp-server",
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
    // Check if authenticated
    if (!emailClient.isAuthenticated()) {
      return {
        content: [
          {
            type: "text",
            text: "Error: Gmail not authenticated. Please run the authentication flow first.",
          },
        ],
      };
    }

    // Execute the tool
    const result = await tool.handler(emailClient, args || {});

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
  console.error("Email MCP Server starting...");

  // Try to load existing token
  try {
    await emailClient.loadToken();
    console.error("✓ Gmail authenticated");
  } catch (error) {
    console.error("⚠ Gmail not authenticated. Run authentication first:");
    console.error("  npm run authenticate");
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Email MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
