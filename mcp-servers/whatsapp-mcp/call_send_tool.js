#!/usr/bin/env node
/**
 * WhatsApp MCP Tool Caller
 *
 * Simple wrapper to call the WhatsApp MCP server's send_message tool
 * without needing a full MCP client implementation.
 *
 * Usage:
 *   node call_send_tool.js "Contact Name" "Your message here"
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { fileURLToPath } from "url";
import { dirname } from "path";
import { spawn } from "child_process";
import fs from "fs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Configuration - use absolute path from current file location
const MCP_SERVER_PATH = process.cwd() + "/dist/index.js";
const DRY_RUN = process.env.WHATSAPP_DRY_RUN !== "false";

/**
 * Send WhatsApp message via MCP server
 */
async function sendWhatsAppMessage(contact, message) {
  console.error(`[WhatsApp] Starting message send...`);
  console.error(`[WhatsApp] To: ${contact}`);
  console.error(`[WhatsApp] Message length: ${message.length} chars`);
  console.error(`[WhatsApp] Dry Run: ${DRY_RUN}`);

  // Check if MCP server is built
  console.error(`[WhatsApp] MCP_SERVER_PATH: ${MCP_SERVER_PATH}`);
  console.error(`[WhatsApp] Exists: ${fs.existsSync(MCP_SERVER_PATH)}`);
  if (!fs.existsSync(MCP_SERVER_PATH)) {
    return {
      success: false,
      message: "WhatsApp MCP server not built. Run 'npm run build' in mcp-servers/whatsapp-mcp/",
      platform: "WhatsApp",
      error: "MCP server not found"
    };
  }

  let client = null;
  let serverProcess = null;

  try {
    // Start the MCP server as a subprocess
    console.error(`[WhatsApp] Starting MCP server...`);
    serverProcess = spawn("node", [MCP_SERVER_PATH], {
      stdio: ["pipe", "pipe", "inherit"], // stdin, stdout, stderr
      cwd: __dirname
    });

    // Create client connected to the server
    const transport = new StdioClientTransport({
      stderr: "inherit"
    });

    // Connect the transport to the server process
    transport.serverProcess = serverProcess;

    client = new Client({
      name: "whatsapp-wrapper-client",
      version: "1.0.0"
    }, {
      capabilities: {}
    });

    await client.connect(transport);
    console.error("[WhatsApp] Connected to MCP server");

    // List available tools first
    const toolsResult = await client.listTools();
    console.error(`[WhatsApp] Available tools: ${toolsResult.tools.map(t => t.name).join(", ")}`);

    // Check if send_message tool exists
    const sendTool = toolsResult.tools.find(t => t.name === "send_message");
    if (!sendTool) {
      throw new Error("send_message tool not available in MCP server");
    }

    // Call the send_message tool
    console.error("[WhatsApp] Calling send_message tool...");
    const result = await client.callTool({
      name: "send_message",
      arguments: {
        contact: contact,
        message: message
      }
    });

    // Extract the response text
    const responseText = result.content.map(c => c.text).join("\n");
    console.error(`[WhatsApp] Response: ${responseText}`);

    // Close the connection
    await client.close();

    // Kill the server process
    if (serverProcess) {
      serverProcess.kill();
    }

    return {
      success: true,
      message: responseText,
      platform: "WhatsApp",
      contact: contact,
      dryRun: DRY_RUN
    };

  } catch (error) {
    console.error(`[WhatsApp] Error: ${error.message}`);

    // Clean up
    if (client) {
      try {
        await client.close();
      } catch {}
    }

    if (serverProcess) {
      serverProcess.kill();
    }

    return {
      success: false,
      message: error.message,
      platform: "WhatsApp",
      error: error.message
    };
  }
}

/**
 * Main
 */
async function main() {
  const contact = process.argv[2];
  const message = process.argv[3];

  if (!contact || !message) {
    console.error("Usage: node call_send_tool.js \"<Contact Name>\" \"<Message>\"");
    process.exit(1);
  }

  const result = await sendWhatsAppMessage(contact, message);

  // Output result as JSON
  console.log(JSON.stringify(result, null, 2));

  process.exit(result.success ? 0 : 1);
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
