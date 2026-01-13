#!/usr/bin/env node
/**
 * Test Calendar MCP - List upcoming events
 */

import { google } from "googleapis";
import { readFileSync } from "fs";
import { OAuth2Client } from "google-auth-library";

async function testCalendar() {
  console.log("🔐 Testing Calendar MCP...\n");

  try {
    // Load token and credentials
    const tokenData = JSON.parse(readFileSync(".calendar_mcp_token.json", "utf-8"));
    const credentials = JSON.parse(readFileSync("credentials.json", "utf-8"));

    // Create OAuth2 client with credentials
    const oauth2Client = new OAuth2Client(
      credentials.installed.client_id,
      credentials.installed.client_secret,
      "urn:ietf:wg:oauth:2.0:oob"
    );
    oauth2Client.setCredentials(tokenData);

    // Create Calendar client
    const calendar = google.calendar({ version: "v3", auth: oauth2Client });

    console.log("1. Testing authentication...");
    const calendarList = await calendar.calendarList.list();

    console.log("✅ Authenticated!");
    const calendars = calendarList.data.items || [];
    console.log(`   Found ${calendars.length} calendars:\n`);

    calendars.slice(0, 3).forEach((cal, i) => {
      console.log(`   ${i + 1}. ${cal.summary}`);
    });

    console.log("\n2. Fetching upcoming events...");
    const now = new Date();
    const timeMax = new Date(now.getTime() + 24 * 60 * 60 * 1000);

    const eventsList = await calendar.events.list({
      calendarId: "primary",
      timeMin: now.toISOString(),
      timeMax: timeMax.toISOString(),
      maxResults: 10,
      singleEvents: true,
      orderBy: "startTime",
    });

    const events = eventsList.data.items || [];
    console.log(`✅ Found ${events.length} upcoming events:\n`);

    if (events.length > 0) {
      events.slice(0, 5).forEach((event, i) => {
        console.log(`   ${i + 1}. ${event.summary}`);
        const start = event.start.dateTime || event.start.date;
        console.log(`      Start: ${start}`);
        if (event.location) {
          console.log(`      Location: ${event.location}`);
        }
        console.log("");
      });
    } else {
      console.log("   No upcoming events found.\n");
    }

    console.log("✅ Calendar MCP is working!\n");

  } catch (error) {
    console.error("❌ Error:", error.message);
    if (error.message.includes("invalid_grant")) {
      console.error("\n💡 Token expired. Run authentication again:");
      console.error("   cd mcp-servers/calendar-mcp && npm run authenticate");
    }
    process.exit(1);
  }
}

testCalendar();
