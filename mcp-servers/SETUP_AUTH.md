# MCP Server Authentication Setup Guide

This guide walks you through setting up OAuth authentication for the MCP servers.

---

## 1. Gmail & Calendar API (Google)

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable APIs:
   - Gmail API
   - Google Calendar API

### Step 2: Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Application type: **Desktop app**
4. Name: `AI Employee MCP`
5. Click **Create**

### Step 3: Download Credentials

1. Download the JSON file
2. Save as: `credentials.json` in the project root

### Step 4: Run Authentication

```bash
# Gmail Authentication
cd mcp-servers/email-mcp
npm run authenticate

# Calendar Authentication
cd mcp-servers/calendar-mcp
npm run authenticate
```

**What will happen:**
1. A URL will be printed
2. Open it in your browser
3. Log in to Google and authorize
4. Copy the authorization code
5. Paste it in the terminal
6. Token will be saved as `.gmail_mcp_token.json` or `.calendar_mcp_token.json`

---

## 2. Xero API

### Step 1: Create Xero App

1. Go to [Xero Developer Portal](https://developer.xero.com/app/manage)
2. Click **New App**
3. Fill in:
   - **App name**: AI Employee MCP
   - **App type**: **Public**
   - **Callback URL**: `http://localhost:3000/callback`
4. Save the **Client ID** and **Client Secret**

### Step 2: Create .env File

Create `.env` in the project root:

```env
XERO_CLIENT_ID=your_client_id_here
XERO_CLIENT_SECRET=your_client_secret_here
XERO_REDIRECT_URI=http://localhost:3000/callback
```

### Step 3: Run Authentication

```bash
cd mcp-servers/xero-mcp
npm run authenticate
```

**What will happen:**
1. A URL will be printed
2. Open it in your browser
3. Log in to Xero
4. Select your organization
5. Authorize the app
6. Token will be automatically saved as `.xero_mcp_token.json`

---

## 3. Verify Tokens

After authentication, you should have:

```
AI_Employee_Vault/
├── credentials.json              # Google OAuth credentials
├── .gmail_mcp_token.json         # Gmail API token
├── .calendar_mcp_token.json      # Calendar API token
├── .xero_mcp_token.json          # Xero API token
└── .env                          # Xero credentials
```

---

## Troubleshooting

### "credentials.json not found"
- Make sure you saved it in the project root
- File name must be exactly `credentials.json`

### "Invalid authorization code"
- Make sure you copied the entire code from the browser
- Codes expire after a few minutes

### Xero callback fails
- Make sure port 3000 is not in use
- Check that your callback URL in Xero matches: `http://localhost:3000/callback`

---

## Quick Start Script

Run all authentications at once:

```bash
# Gmail
cd mcp-servers/email-mcp && npm run authenticate && cd ../..

# Calendar
cd mcp-servers/calendar-mcp && npm run authenticate && cd ../..

# Xero
cd mcp-servers/xero-mcp && npm run authenticate && cd ../..
```
