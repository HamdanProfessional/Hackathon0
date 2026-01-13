#!/usr/bin/env node
/**
 * Xero Authentication Script
 *
 * Run this script to authenticate with Xero OAuth 2.0.
 * Generates a token file that the MCP server uses.
 */

import { XeroClient } from "xero-node";
import { createServer } from "http";
import { readFileSync, writeFileSync } from "fs";
import dotenv from "dotenv";
import { URL } from "url";

dotenv.config();

const __dirname = new URL(".", import.meta.url).pathname;

// Xero client config
const config = {
  clientId: process.env.XERO_CLIENT_ID || "",
  clientSecret: process.env.XERO_CLIENT_SECRET || "",
  redirectUris: [process.env.XERO_REDIRECT_URI || "http://localhost:3000/callback"],
  scopes: [
    "offline_access",
    "accounting.transactions",
    "accounting.reports.read",
    "accounting.settings",
  ],
};

if (!config.clientId || !config.clientSecret) {
  console.error("❌ Error: XERO_CLIENT_ID and XERO_CLIENT_SECRET must be set in .env");
  process.exit(1);
}

const xero = new XeroClient(config);

// Create a simple HTTP server for the callback
const server = createServer(async (req, res) => {
  if (req.url?.startsWith("/callback")) {
    try {
      const url = new URL(req.url, `http://${req.headers.host}`);

      // Exchange code for token
      await xero.apiCallback(url.toString());

      // Get tenants (wrap in try-catch in case of scope issues)
      let tenantId;
      try {
        const tenants = await xero.updateTenants();

        if (tenants.length === 0) {
          res.writeHead(500, { "Content-Type": "text/html" });
          res.end("<h1>Error: No Xero organizations found</h1>");
          server.close();
          return;
        }

        // Use first tenant
        tenantId = tenants[0].tenantId;
      } catch (tenantError: any) {
        // If we can't get tenants due to scope issues, try to continue anyway
        console.log("⚠️  Warning: Could not get tenants, but continuing...");
        tenantId = "DEFAULT_TENANT";
      }

      // Save token
      const tokenSet = await xero.readTokenSet();
      const tokenData = {
        access_token: tokenSet.access_token,
        refresh_token: tokenSet.refresh_token,
        expires_at: tokenSet.expires_at,
        tenantId: tenantId,
      };

      writeFileSync(
        ".xero_mcp_token.json",
        JSON.stringify(tokenData, null, 2)
      );

      // Send success response
      res.writeHead(200, { "Content-Type": "text/html" });
      res.end(`
        <h1>✓ Authentication Successful!</h1>
        <p>Token saved to .xero_mcp_token.json</p>
        <p>Tenant ID: ${tenantId}</p>
        <p>You can close this window and return to the terminal.</p>
      `);

      server.close();
    } catch (error: any) {
      console.error("Error during callback:", error.message);
      res.writeHead(500, { "Content-Type": "text/html" });
      res.end(`<h1>Authentication Error</h1><p>${error.message}</p>`);
      server.close();
    }
  }
});

// Start server
const PORT = 3000;
server.listen(PORT, async () => {
  console.log("🔐 Xero Authentication");
  console.log("==================");
  console.log(`\nCallback server listening on port ${PORT}\n`);

  // Generate consent URL
  const consentUrl = await xero.buildConsentUrl();

  console.log("1. Open this URL in your browser:\n");
  console.log(consentUrl + "\n");

  console.log("2. Log in to Xero and select your organization\n");

  console.log("3. After authorization, you'll be redirected back here\n");

  console.log("4. The token will be saved automatically\n");

  console.log("\nWaiting for authorization...\n");
});
