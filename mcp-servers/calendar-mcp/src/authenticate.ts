#!/usr/bin/env node
/**
 * Google Calendar Authentication Script
 *
 * Run this script to authenticate with Google Calendar OAuth 2.0.
 */

import { google } from "googleapis";
import { OAuth2Client } from "google-auth-library";
import { readFileSync, writeFileSync, existsSync } from "fs";
import { createInterface } from "readline";

const rl = createInterface({
  input: process.stdin,
  output: process.stdout,
});

function question(query: string): Promise<string> {
  return new Promise((resolve) => {
    rl.question(query, (answer) => {
      resolve(answer);
    });
  });
}

async function authenticate() {
  console.log("🔐 Google Calendar Authentication");
  console.log("===========================\n");

  // Check if credentials file exists
  const credentialsPath = process.env.GOOGLE_CREDENTIALS_PATH || "credentials.json";

  if (!existsSync(credentialsPath)) {
    console.error(`❌ Error: Credentials file not found at ${credentialsPath}`);
    console.error("\nPlease download your OAuth credentials from Google Cloud Console");
    console.error("and save them as credentials.json in the project root.\n");
    process.exit(1);
  }

  // Load credentials
  const credentials = JSON.parse(readFileSync(credentialsPath, "utf-8"));

  // Create OAuth client
  const client = new OAuth2Client(
    credentials.installed.client_id,
    credentials.installed.client_secret,
    "urn:ietf:wg:oauth:2.0:oob"
  );

  // Generate auth URL
  const authUrl = client.generateAuthUrl({
    access_type: "offline",
    scope: [
      "https://www.googleapis.com/auth/calendar",
      "https://www.googleapis.com/auth/calendar.events",
    ],
  });

  console.log("1. Open this URL in your browser:\n");
  console.log(authUrl + "\n");

  console.log("2. Log in to your Google account and authorize the app\n");

  const code = await question("3. Enter the authorization code: ");

  // Exchange code for tokens
  console.log("\nExchanging code for tokens...");

  await client.getToken(code);

  // Save token
  const tokenPath = process.env.CALENDAR_TOKEN_PATH || ".calendar_mcp_token.json";
  writeFileSync(tokenPath, JSON.stringify(client.credentials, null, 2));

  console.log("\n✓ Authentication successful!");
  console.log(`Token saved to ${tokenPath}\n`);

  // Test the connection
  try {
    const calendar = google.calendar({ version: "v3", auth: client });
    const calendarList = await calendar.calendarList.list();

    console.log("✓ Connection verified!");
    console.log(`   Calendars: ${calendarList.data.items?.length || 0}\n`);

    if (calendarList.data.items && calendarList.data.items.length > 0) {
      console.log("   Available calendars:");
      calendarList.data.items.slice(0, 3).forEach((cal: any) => {
        console.log(`   - ${cal.summary} (${cal.primary ? "primary" : ""})`);
      });
    }
  } catch (error) {
    console.error("⚠ Warning: Could not verify connection:", error);
  }

  rl.close();
}

authenticate().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
