#!/usr/bin/env node
/**
 * Test Slack Bot Token
 */

import { WebClient } from "@slack/web-api";
import dotenv from "dotenv";
import { readFileSync } from "fs";

dotenv.config();

const token = process.env.SLACK_BOT_TOKEN;

if (!token) {
  console.error("❌ SLACK_BOT_TOKEN not found in .env");
  process.exit(1);
}

console.log("🔐 Testing Slack Bot Token...\n");

const web = new WebClient(token);

async function testConnection() {
  try {
    // Test 1: Get auth info
    console.log("1. Testing bot authentication...");
    const authResult = await web.auth.test();
    console.log("✅ Bot authenticated!");
    console.log(`   Bot Name: ${authResult.user || authResult.data?.user}`);
    console.log(`   Team: ${authResult.team || authResult.data?.team}`);
    console.log(`   Team ID: ${authResult.team_id || authResult.data?.team_id}\n`);

    // Test 2: Get team info
    console.log("2. Fetching team info...");
    const teamResult = await web.team.info();
    const team = teamResult.team || teamResult.data?.team;
    console.log("✅ Team info retrieved!");
    console.log(`   Team Domain: ${team.domain}`);
    console.log(`   Team Name: ${team.name}\n`);

    // Test 3: List channels
    console.log("3. Listing channels...");
    const channelsResult = await web.conversations.list({
      types: ["public_channel", "private_channel", "mpim"],
      limit: 10,
    });
    const channels = channelsResult.channels || channelsResult.data?.channels;
    console.log("✅ Channels retrieved!");
    console.log(`   Found: ${channels.length} channels\n`);

    if (channels.length > 0) {
      console.log("   Recent channels:");
      channels.slice(0, 5).forEach((channel, i) => {
        console.log(`   ${i + 1}. #${channel.name} - ${channel.is_private ? '(Private)' : '(Public)'}`);
      });
    }

    console.log("\n✅ All tests passed! Bot is ready.\n");
    console.log("📝 Token verified and saved to .env");
    console.log("🚀 You can now use Slack MCP with Claude Code!\n");

  } catch (error) {
    console.error("\n❌ Error:", error.message);
    if (error.data && error.data.error) {
      console.error(`   Error Code: ${error.data.error}`);
    }
    process.exit(1);
  }
}

testConnection();
