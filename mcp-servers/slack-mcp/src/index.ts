#!/usr/bin/env node
/**
 * Slack MCP Server
 *
 * Model Context Protocol server for Slack integration.
 * Provides tools for sending messages and managing Slack communications.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import dotenv from "dotenv";
import { SlackClient } from "./slack-client.js";
import { tools } from "./tools.js";

// Load environment variables
dotenv.config();

// Create Slack client
const slackClient = new SlackClient({
  botToken: process.env.SLACK_BOT_TOKEN || "",
});

// Create MCP server
const server = new Server(
  {
    name: "slack-mcp-server",
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
    if (!(await slackClient.isAuthenticated())) {
      return {
        content: [
          {
            type: "text",
            text: "Error: Slack not authenticated. Please check SLACK_BOT_TOKEN environment variable.",
          },
        ],
        isError: true,
      };
    }

    // Execute the tool
    const result = await tool.handler(slackClient, args || {});

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
  console.error("Slack MCP Server starting...");

  // Check authentication
  if (process.env.SLACK_BOT_TOKEN) {
    const authResult = await slackClient.isAuthenticated();
    if (authResult) {
      console.error("✓ Slack authenticated");
    }
  } else {
    console.error("⚠ SLACK_BOT_TOKEN not set. Set environment variable to enable Slack integration.");
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Slack MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
