#!/usr/bin/env node
/**
 * Simple Slack Bot Token Verification
 */

import { WebClient } from "@slack/web-api";
import dotenv from "dotenv";

dotenv.config();

const token = process.env.SLACK_BOT_TOKEN;

if (!token || !token.startsWith("xoxb-")) {
  console.error("❌ Invalid SLACK_BOT_TOKEN (must start with xoxb-)");
  process.exit(1);
}

console.log("🔐 Verifying Slack Bot Token...\n");

const web = new WebClient(token);

async function verify() {
  try {
    const result = await web.auth.test();

    console.log("✅ Bot Token Valid!\n");
    console.log(`Bot Name: ${result.user || result.data?.user}`);
    console.log(`Team: ${result.team || result.data?.team}`);
    console.log(`Team ID: ${result.team_id || result.data?.team_id}\n`);
    console.log("📝 Slack MCP is ready to use!\n");
    console.log("You can now use Claude Code to:");
    console.log("  - Send messages to Slack channels");
    console.log("  - List channels and users");
    console.log("  - Get channel information");
    console.log("  - Read message history\n");

  } catch (error) {
    console.error("❌ Error:", error.message);
    process.exit(1);
  }
}

verify();
