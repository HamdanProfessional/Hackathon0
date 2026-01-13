#!/usr/bin/env node
/**
 * Test Slack Bot - List Channels and Send Test Message
 */

import { WebClient } from "@slack/web-api";
import dotenv from "dotenv";

dotenv.config();

const token = process.env.SLACK_BOT_TOKEN;

if (!token) {
  console.error("❌ SLACK_BOT_TOKEN not found in .env");
  process.exit(1);
}

console.log("🔐 Testing Slack Bot...\n");

const web = new WebClient(token);

async function testSlack() {
  try {
    // Test 1: Get auth info
    console.log("1. Testing bot authentication...");
    const authResult = await web.auth.test();
    console.log("✅ Bot authenticated!");
    console.log(`   Bot Name: ${authResult.user || authResult.data?.user}`);
    console.log(`   Team: ${authResult.team || authResult.data?.team}\n`);

    // Test 2: List channels
    console.log("2. Listing channels...");
    const channelsResult = await web.conversations.list({
      types: "public_channel,private_channel",
      limit: 20,
    });
    const channels = channelsResult.channels || channelsResult.data?.channels || [];
    console.log(`✅ Found ${channels.length} channels:\n`);

    if (channels.length > 0) {
      channels.slice(0, 10).forEach((channel, i) => {
        const type = channel.is_private ? '🔒' : '🌐';
        console.log(`   ${i + 1}. ${type} #${channel.name}`);
      });
    }

    console.log("\n✅ Slack MCP is working!\n");

  } catch (error) {
    console.error("\n❌ Error:", error.message);
    if (error.data && error.data.error) {
      console.error(`   Error Code: ${error.data.error}`);
      if (error.data.error === "missing_scope") {
        console.error("\n💡 Tip: Make sure your bot has these scopes in OAuth & Permissions:");
        console.error("   - channels:read");
        console.error("   - groups:read");
        console.error("   - chat:write");
        console.error("   - im:read");
        console.error("   - mpim:read");
      }
    }
    process.exit(1);
  }
}

testSlack();
