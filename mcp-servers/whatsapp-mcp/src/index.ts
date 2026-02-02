#!/usr/bin/env node
/**
 * WhatsApp MCP Server
 *
 * Model Context Protocol server for WhatsApp integration.
 * Provides tools for sending messages and managing WhatsApp communications
 * via Playwright browser automation.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import dotenv from "dotenv";
import { WhatsAppClient } from "./whatsapp-client.js";
import { tools } from "./tools.js";

// Load environment variables
dotenv.config();

// Create WhatsApp client
const whatsappClient = new WhatsAppClient({
  sessionPath: process.env.WHATSAPP_SESSION_PATH || "./whatsapp_mcp_session",
  headless: process.env.WHATSAPP_HEADLESS === "true",
});

// Create MCP server
const server = new Server(
  {
    name: "whatsapp-mcp-server",
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
    // Special handling for check_status (doesn't require connection)
    if (name === "check_status") {
      const result = await tool.handler(whatsappClient, args || {});

      return {
        content: [
          {
            type: "text",
            text: result,
          },
        ],
      };
    }

    // Check if connected
    if (!whatsappClient.getConnectedStatus()) {
      // Try to connect
      const connected = await whatsappClient.connect();
      if (!connected) {
        return {
          content: [
            {
              type: "text",
              text: "Error: WhatsApp not connected. Please scan QR code in the browser window.",
            },
          ],
          isError: true,
        };
      }
    }

    // Execute the tool
    const result = await tool.handler(whatsappClient, args || {});

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
  console.error("WhatsApp MCP Server starting...");

  // Create session directory if it doesn't exist
  const fs = await import("fs");
  const path = await import("path");
  const sessionPath = process.env.WHATSAPP_SESSION_PATH || "./whatsapp_mcp_session";

  if (!fs.existsSync(sessionPath)) {
    fs.mkdirSync(sessionPath, { recursive: true });
    console.error(`✓ Created session directory: ${sessionPath}`);
  }

  // Try to connect on startup
  console.error("Attempting to connect to WhatsApp Web...");
  try {
    const connected = await whatsappClient.connect();
    if (connected) {
      console.error("✓ WhatsApp connected and ready");
    } else {
      console.error("⚠ WhatsApp requires authentication. Please scan QR code in browser window.");
      console.error("⚠ The server will wait for authentication before processing requests.");
    }
  } catch (error) {
    console.error("⚠ Could not auto-connect to WhatsApp:", error);
    console.error("⚠ Will attempt connection when tools are called.");
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("WhatsApp MCP Server running on stdio");
}

// Graceful shutdown
async function shutdown() {
  console.error("Shutting down WhatsApp MCP Server...");
  await whatsappClient.close();
  process.exit(0);
}

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);

main().catch((error) => {
  console.error("Fatal error:", error);
  shutdown();
});
