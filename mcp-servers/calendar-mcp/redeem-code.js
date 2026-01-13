#!/usr/bin/env node
/**
 * Redeem Calendar Authorization Code
 */

import { google } from "googleapis";
import { OAuth2Client } from "google-auth-library";
import { readFileSync, writeFileSync } from "fs";

const code = "4/1ASc3gC3ZGb9AcdlkhNK1S4IF9czywDLVOtj_RU53fdKFG6qEQbSIsDtXbdE";

async function redeemCode() {
  console.log("🔐 Redeeming Calendar authorization code...\n");

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
  console.log("Tokens received");

  // Save token
  writeFileSync(".calendar_mcp_token.json", JSON.stringify(tokens, null, 2));

  console.log("\n✅ Authentication successful!");
  console.log("Token saved to .calendar_mcp_token.json\n");

  // Set credentials for testing
  client.setCredentials(tokens);

  // Test the connection
  try {
    const calendar = google.calendar({ version: "v3", auth: client });
    const calendarList = await calendar.calendarList.list();

    console.log("✅ Connection verified!");
    const calendars = calendarList.data.items || [];
    console.log(`   Found ${calendars.length} calendars\n`);
  } catch (error) {
    console.error("⚠ Warning: Could not verify connection:", error.message);
  }
}

redeemCode().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
