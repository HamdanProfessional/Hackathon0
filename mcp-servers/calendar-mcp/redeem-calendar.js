#!/usr/bin/env node
/**
 * Test Calendar using Gmail credentials
 */

import { google } from "googleapis";
import { readFileSync } from "fs";
import { OAuth2Client } from "google-auth-library";

async function testCalendarWithGmailToken() {
  console.log("🔐 Testing Calendar MCP with Gmail token...\n");

  try {
    // Load Gmail token and credentials
    const tokenData = JSON.parse(readFileSync("../email-mcp/.gmail_mcp_token.json", "utf-8"));
    const credentials = JSON.parse(readFileSync("../email-mcp/credentials.json", "utf-8"));

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

    // Save the token for calendar-mcp
    const { writeFileSync } = await import("fs");
    writeFileSync(".calendar_mcp_token.json", JSON.stringify(tokenData, null, 2));
    console.log("✅ Calendar MCP is working! Token saved.\n");

  } catch (error) {
    console.error("❌ Error:", error.message);
    if (error.message.includes("Calendar API has not been used")) {
      console.error("\n💡 Calendar API needs to be enabled. Open this link:");
      console.error("   https://console.developers.google.com/apis/api/calendar-json.googleapis.com/overview?project=1047374580620");
    }
    process.exit(1);
  }
}

testCalendarWithGmailToken();
