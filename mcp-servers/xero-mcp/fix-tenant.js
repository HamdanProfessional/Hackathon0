#!/usr/bin/env node
/**
 * Fix Xero Tenant ID
 */

import { XeroClient } from "xero-node";
import { readFileSync, writeFileSync } from "fs";
import dotenv from "dotenv";

dotenv.config();

async function fixTenant() {
  console.log("🔐 Fixing Xero Tenant ID...\n");

  // Load token
  const tokenData = JSON.parse(readFileSync(".xero_mcp_token.json", "utf-8"));

  // Create Xero client
  const xero = new XeroClient({
    clientId: process.env.XERO_CLIENT_ID || "",
    clientSecret: process.env.XERO_CLIENT_SECRET || "",
    redirectUris: [process.env.XERO_REDIRECT_URI || "http://localhost:3000/callback"],
    scopes: ["offline_access", "accounting.transactions", "accounting.reports.read"],
  });

  // Set token
  await xero.setTokenSet({
    access_token: tokenData.access_token,
    refresh_token: tokenData.refresh_token,
    expires_at: new Date(tokenData.expires_at * 1000),
  });

  console.log("1. Fetching tenants...");
  try {
    const tenants = await xero.updateTenants();

    if (tenants.length === 0) {
      console.error("❌ No tenants found. Make sure you have a Xero organization.");
      process.exit(1);
    }

    const tenantId = tenants[0].tenantId;
    console.log(`✅ Found tenant: ${tenantId}`);
    console.log(`   Tenant Name: ${tenants[0].tenantName}\n`);

    // Update token file with correct tenant ID
    tokenData.tenantId = tenantId;
    writeFileSync(".xero_mcp_token.json", JSON.stringify(tokenData, null, 2));

    console.log("✅ Tenant ID updated in token file!\n");

    // Test connection
    console.log("2. Testing API connection...");
    const response = await xero.accountingApi.getInvoices(tenantId);
    const invoices = response.body?.invoices || [];
    console.log(`✅ Connection successful! Found ${invoices.length} invoices.\n`);

  } catch (error) {
    console.error("❌ Error:", error.message);
    console.error("\n⚠ Could not fetch tenants. Keeping DEFAULT_TENANT.");
    console.error("The Xero MCP may not work correctly without a valid tenant ID.\n");
    process.exit(1);
  }
}

fixTenant();
