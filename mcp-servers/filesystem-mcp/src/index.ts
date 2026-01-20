#!/usr/bin/env node
/**
 * Filesystem MCP Server
 *
 * Model Context Protocol server for filesystem operations.
 * Provides tools for watching directories, reading/writing files, and file management.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import dotenv from "dotenv";
import { FilesystemClient } from "./filesystem-client.js";
import { tools } from "./tools.js";

// Load environment variables
dotenv.config();

// Get base directory from environment or use current directory
const BASE_DIR = process.env.FILESYSTEM_BASE_DIR || process.cwd();

// Create filesystem client
const fsClient = new FilesystemClient();

// Log startup
console.error(`Filesystem MCP Server starting...`);
console.error(`Base directory: ${BASE_DIR}`);

// Create MCP server
const server = new Server(
  {
    name: "filesystem-mcp-server",
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
    // Execute the tool
    const result = await tool.handler(fsClient, args || {});

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
    console.error(`Error executing tool ${name}:`, errorMessage);

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
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error("Filesystem MCP Server running on stdio");
  console.error("Available tools:", tools.map((t) => t.name).join(", "));

  // Graceful shutdown
  process.on("SIGINT", () => {
    console.error("\nShutting down Filesystem MCP Server...");
    fsClient.stopAllWatchers();
    process.exit(0);
  });
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});
