#!/usr/bin/env node
/**
 * Test Gmail MCP - List recent emails
 */

import { EmailClient } from "./dist/email-client.js";
import { google } from "googleapis";
import { readFileSync } from "fs";
import { OAuth2Client } from "google-auth-library";

async function testGmail() {
  console.log("🔐 Testing Gmail MCP...\n");

  try {
    // Load token and credentials
    const tokenData = JSON.parse(readFileSync(".gmail_mcp_token.json", "utf-8"));
    const credentials = JSON.parse(readFileSync("credentials.json", "utf-8"));

    // Create OAuth2 client with credentials
    const oauth2Client = new OAuth2Client(
      credentials.installed.client_id,
      credentials.installed.client_secret,
      "urn:ietf:wg:oauth:2.0:oob"
    );
    oauth2Client.setCredentials(tokenData);

    // Create Gmail client
    const gmail = google.gmail({ version: "v1", auth: oauth2Client });

    console.log("1. Testing authentication...");
    const profile = await gmail.users.getProfile({ userId: "me" });
    console.log("✅ Authenticated!");
    console.log(`   Email: ${profile.data.emailAddress}`);
    console.log(`   Messages: ${profile.data.messagesTotal}`);
    console.log(`   Threads: ${profile.data.threadsTotal}\n`);

    console.log("2. Fetching recent emails...");
    const response = await gmail.users.messages.list({
      userId: "me",
      maxResults: 5,
    });

    const messages = response.data.messages || [];
    console.log(`✅ Found ${messages.length} recent emails:\n`);

    if (messages.length > 0) {
      // Fetch full details for each message
      for (let i = 0; i < Math.min(messages.length, 5); i++) {
        const msg = messages[i];
        const full = await gmail.users.messages.get({
          userId: "me",
          id: msg.id,
          format: "metadata",
          metadataHeaders: ["From", "Subject", "Date"],
        });

        const headers = full.data.payload.headers;
        const from = headers.find(h => h.name === "From")?.value || "Unknown";
        const subject = headers.find(h => h.name === "Subject")?.value || "No Subject";
        const date = headers.find(h => h.name === "Date")?.value || "Unknown";

        console.log(`   ${i + 1}. From: ${from}`);
        console.log(`      Subject: ${subject}`);
        console.log(`      Date: ${date}\n`);
      }
    } else {
      console.log("   No recent emails found.\n");
    }

    console.log("✅ Gmail MCP is working!\n");

  } catch (error) {
    console.error("❌ Error:", error.message);
    if (error.message.includes("invalid_grant")) {
      console.error("\n💡 Token expired. Run authentication again:");
      console.error("   cd mcp-servers/email-mcp && npm run authenticate");
    }
    process.exit(1);
  }
}

testGmail();
