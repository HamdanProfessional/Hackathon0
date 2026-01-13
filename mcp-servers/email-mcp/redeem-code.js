#!/usr/bin/env node
/**
 * Redeem Gmail Authorization Code
 */

import { google } from "googleapis";
import { OAuth2Client } from "google-auth-library";
import { readFileSync, writeFileSync } from "fs";

const code = "4/1ASc3gC0SsY1AkJra12jWGFUWAEsNJHxK2-FnCbdy9HJEXEaXWo0gvBzyeuI";

async function redeemCode() {
  console.log("🔐 Redeeming Gmail authorization code...\n");

  // Load credentials
  const credentials = JSON.parse(readFileSync("credentials.json", "utf-8"));

  // Create OAuth client
  const client = new OAuth2Client(
    credentials.installed.client_id,
    credentials.installed.client_secret,
    "urn:ietf:wg:oauth:2.0:oob"
  );

  // Exchange code for tokens
  console.log("Exchanging code for tokens...");
  const { tokens } = await client.getToken(code);
  console.log("Tokens received:", tokens);

  // Save token
  writeFileSync(".gmail_mcp_token.json", JSON.stringify(tokens, null, 2));

  console.log("\n✅ Authentication successful!");
  console.log("Token saved to .gmail_mcp_token.json\n");

  // Set credentials for testing
  client.setCredentials(tokens);

  // Test the connection
  try {
    const gmail = google.gmail({ version: "v1", auth: client });
    const profile = await gmail.users.getProfile({ userId: "me" });

    console.log("✅ Connection verified!");
    console.log(`   Email: ${profile.data.emailAddress}`);
    console.log(`   Messages: ${profile.data.messagesTotal}\n`);
  } catch (error) {
    console.error("⚠ Warning: Could not verify connection:", error.message);
  }
}

redeemCode().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
