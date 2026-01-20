#!/usr/bin/env node
/**
 * Test script for Filesystem MCP Server
 */

const { spawn } = require("child_process");
const path = require("path");

console.log("Testing Filesystem MCP Server...\n");

// Test 1: List tools
console.log("Test 1: Listing available tools");
const mcpPath = path.join(__dirname, "dist", "index.js");

const testMCP = () => {
  return new Promise((resolve, reject) => {
    const mcp = spawn("node", [mcpPath], {
      cwd: __dirname,
      env: { ...process.env, FILESYSTEM_BASE_DIR: path.join(__dirname, "..", "..", "..") },
    });

    let output = "";
    let errorOutput = "";

    mcp.stdout.on("data", (data) => {
      output += data.toString();
    });

    mcp.stderr.on("data", (data) => {
      const text = data.toString();
      errorOutput += text;
      // Log stderr for debugging
      if (!text.includes("Filesystem MCP Server running")) {
        process.stderr.write(text);
      }
    });

    // Send list_tools request
    setTimeout(() => {
      mcp.stdin.write(JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "tools/list",
      }) + "\n");
    }, 100);

    // Test read_file tool
    setTimeout(() => {
      mcp.stdin.write(JSON.stringify({
        jsonrpc: "2.0",
        id: 2,
        method: "tools/call",
        params: {
          name: "list_directory",
          arguments: {
            path: "../../AI_Employee_Vault"
          }
        }
      }) + "\n");
    }, 500);

    setTimeout(() => {
      mcp.stdin.end();
    }, 2000);

    mcp.on("close", (code) => {
      console.log(`\nMCP Server exited with code ${code}`);
      if (errorOutput.includes("Filesystem MCP Server running")) {
        console.log("\n✅ MCP Server started successfully!");
      }
      resolve();
    });

    mcp.on("error", (error) => {
      reject(error);
    });
  });
};

// Run test
testMCP().then(() => {
  console.log("\n✅ Tests completed!");
  process.exit(0);
}).catch((error) => {
  console.error("\n❌ Test failed:", error);
  process.exit(1);
});
