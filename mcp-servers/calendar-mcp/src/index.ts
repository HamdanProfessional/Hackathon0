#!/usr/bin/env node
/**
 * Calendar MCP Server
 *
 * Model Context Protocol server for Google Calendar integration.
 * Provides tools for creating events, managing schedule, and calendar operations.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import dotenv from "dotenv";
import { CalendarClient } from "./calendar-client.js";
import { tools } from "./tools.js";

// Load environment variables
dotenv.config();

// Create calendar client
const calendarClient = new CalendarClient({
  credentialsPath: process.env.GOOGLE_CREDENTIALS_PATH || ".",
  tokenPath: process.env.CALENDAR_TOKEN_PATH || ".calendar_mcp_token.json",
});

// Create MCP server
const server = new Server(
  {
    name: "calendar-mcp-server",
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
    if (!calendarClient.isAuthenticated()) {
      return {
        content: [
          {
            type: "text",
            text: "Error: Calendar not authenticated. Please run the authentication flow first.",
          },
        ],
      };
    }

    // Execute the tool
    const result = await tool.handler(calendarClient, args || {});

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
  console.error("Calendar MCP Server starting...");

  // Try to load existing token
  try {
    await calendarClient.loadToken();
    console.error("✓ Calendar authenticated");
  } catch (error) {
    console.error("⚠ Calendar not authenticated. Run authentication first:");
    console.error("  npm run authenticate");
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Calendar MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
