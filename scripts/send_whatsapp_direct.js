#!/usr/bin/env node
/**
 * Direct WhatsApp Message Sender
 *
 * Simple script to send a WhatsApp message using Playwright
 * without going through the MCP server complexity.
 */

const { chromium } = require("playwright");

async function sendWhatsAppMessage(contact, message) {
  console.log(`Sending WhatsApp message to ${contact}...`);

  const browser = await chromium.launch({
    headless: false // Show browser so user can scan QR if needed
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  });

  const page = await context.newPage();

  // Navigate to WhatsApp Web
  console.log("Navigating to WhatsApp Web...");
  await page.goto("https://web.whatsapp.com", {
    waitUntil: "networkidle",
    timeout: 60000
  });

  // Wait for page load
  await page.waitForTimeout(3000);

  // Check if logged in
  const isLoggedIn = await page.evaluate(() => {
    return !!document.querySelector('[data-testid="chat-list"]') ||
           !!document.querySelector('#side') ||
           !!document.querySelector('[data-testid="pane-side"]');
  });

  if (!isLoggedIn) {
    console.log("⚠ Please scan the QR code in the browser window to log in to WhatsApp...");

    // Wait for login (up to 2 minutes)
    try {
      await page.waitForSelector('[data-testid="chat-list"], #side, [data-testid="pane-side"]', {
        timeout: 120000
      });
      console.log("✓ Logged in to WhatsApp!");
    } catch {
      console.log("❌ Login timeout. Please try again.");
      await browser.close();
      process.exit(1);
    }
  } else {
    console.log("✓ Already logged in to WhatsApp!");
  }

  // Search for contact
  console.log(`Searching for contact: ${contact}...`);
  await page.click('[data-testid="chat-list-search"]');
  await page.fill('[data-testid="chat-list-search"]', contact);
  await page.waitForTimeout(1500);

  // Click on the contact
  try {
    const contactSelector = `[data-testid="cell-frame-container"] >> text=${contact}`;
    await page.click(contactSelector, { timeout: 10000 });
    console.log(`✓ Found contact: ${contact}`);
  } catch {
    console.log(`❌ Could not find contact: ${contact}`);
    console.log("Please check the contact name and try again.");
    await browser.close();
    process.exit(1);
  }

  await page.waitForTimeout(1000);

  // Type and send message
  console.log("Sending message...");
  await page.fill('[data-testid="conversation-panel-footer"] >> div[contenteditable="true"]', message);
  await page.click('[data-testid="send-button"]');

  // Wait for send confirmation
  await page.waitForTimeout(2000);

  console.log(`✓ Message sent to ${contact}!`);

  // Keep browser open for a moment so user can see the result
  console.log("Closing browser in 3 seconds...");
  await page.waitForTimeout(3000);

  await browser.close();
  console.log("Done!");
}

// Get command line arguments
const contact = process.argv[2];
const message = process.argv[3];

if (!contact || !message) {
  console.log("Usage: node send_whatsapp_direct.js \"<Contact Name>\" \"<Message>\"");
  console.log("Example: node send_whatsapp_direct.js \"Anus Mehmood\" \"Hi\"");
  process.exit(1);
}

sendWhatsAppMessage(contact, message).catch(error => {
  console.error("Error:", error.message);
  process.exit(1);
});
