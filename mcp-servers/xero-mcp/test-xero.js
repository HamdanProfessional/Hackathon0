#!/usr/bin/env node
/**
 * Test Xero MCP - Query accounts and invoices
 */

import { XeroClient } from "./dist/xero-client.js";
import { readFileSync } from "fs";
import dotenv from "dotenv";

dotenv.config();

async function testXero() {
  console.log("🔐 Testing Xero MCP...\n");

  try {
    // Load token
    const tokenData = JSON.parse(readFileSync(".xero_mcp_token.json", "utf-8"));

    // Create Xero client
    const client = new XeroClient({
      clientId: process.env.XERO_CLIENT_ID || "",
      clientSecret: process.env.XERO_CLIENT_SECRET || "",
      redirectUri: process.env.XERO_REDIRECT_URI || "http://localhost:3000/callback",
      scopes: ["offline_access", "accounting.transactions", "accounting.reports.read"],
    });

    // Load token
    await client.loadToken();

    console.log("1. Testing authentication...");
    console.log("✅ Authenticated!");
    console.log(`   Tenant ID: ${tokenData.tenantId}\n`);

    console.log("2. Fetching overdue invoices...");
    const overdueInvoices = await client.getOverdueInvoices();

    console.log(`✅ Found ${overdueInvoices.length} overdue invoices:\n`);

    if (overdueInvoices.length > 0) {
      overdueInvoices.slice(0, 5).forEach((invoice, i) => {
        console.log(`   ${i + 1}. Invoice #${invoice.invoiceNumber || invoice.invoiceID}`);
        console.log(`      Contact: ${invoice.contact?.name}`);
        console.log(`      Amount: ${invoice.total} ${invoice.currencyCode}`);
        console.log(`      Status: ${invoice.status}`);
        console.log(`      Due: ${invoice.dueDate}\n`);
      });
    } else {
      console.log("   No overdue invoices found.\n");
    }

    console.log("✅ Xero MCP is working!\n");

  } catch (error) {
    const errorMessage = error?.message || String(error);
    console.error("❌ Error:", errorMessage);
    if (errorMessage && (errorMessage.includes("invalid_grant") || errorMessage.includes("401"))) {
      console.error("\n💡 Token expired. Run authentication again:");
      console.error("   cd mcp-servers/xero-mcp && npm run authenticate");
    }
    process.exit(1);
  }
}

testXero();
