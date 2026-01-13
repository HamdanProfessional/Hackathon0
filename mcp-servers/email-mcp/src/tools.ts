/**
 * MCP Tools Definitions
 *
 * Defines all available tools for the Email MCP server.
 */

import { EmailClient } from "./email-client.js";

export interface Tool {
  name: string;
  description: string;
  inputSchema: any;
  handler: (client: EmailClient, args: any) => Promise<string>;
}

/**
 * Send an email
 */
const sendEmailTool: Tool = {
  name: "send_email",
  description: "Send an email to a recipient",
  inputSchema: {
    type: "object",
    properties: {
      to: {
        type: "string",
        description: "Recipient email address",
      },
      subject: {
        type: "string",
        description: "Email subject line",
      },
      body: {
        type: "string",
        description: "Email body content (plain text)",
      },
      cc: {
        type: "string",
        description: "CC recipients (optional, comma-separated)",
      },
      bcc: {
        type: "string",
        description: "BCC recipients (optional, comma-separated)",
      },
    },
    required: ["to", "subject", "body"],
  },
  handler: async (client, args) => {
    try {
      const messageId = await client.sendEmail({
        to: args.to,
        subject: args.subject,
        body: args.body,
        cc: args.cc,
        bcc: args.bcc,
      });

      return `✓ Email sent successfully\nMessage ID: ${messageId}\n\nTo: ${args.to}\nSubject: ${args.subject}`;
    } catch (error) {
      throw new Error(`Failed to send email: ${error}`);
    }
  },
};

/**
 * Create a draft email
 */
const createDraftTool: Tool = {
  name: "create_draft",
  description: "Create a draft email in Gmail (not sent)",
  inputSchema: {
    type: "object",
    properties: {
      to: {
        type: "string",
        description: "Recipient email address",
      },
      subject: {
        type: "string",
        description: "Email subject line",
      },
      body: {
        type: "string",
        description: "Email body content (plain text)",
      },
      cc: {
        type: "string",
        description: "CC recipients (optional, comma-separated)",
      },
      bcc: {
        type: "string",
        description: "BCC recipients (optional, comma-separated)",
      },
    },
    required: ["to", "subject", "body"],
  },
  handler: async (client, args) => {
    try {
      const draftId = await client.createDraft({
        to: args.to,
        subject: args.subject,
        body: args.body,
        cc: args.cc,
        bcc: args.bcc,
      });

      return `✓ Draft created successfully\nDraft ID: ${draftId}\n\nTo: ${args.to}\nSubject: ${args.subject}\n\nNote: Draft saved in Gmail, not sent.`;
    } catch (error) {
      throw new Error(`Failed to create draft: ${error}`);
    }
  },
};

/**
 * Get email details
 */
const getEmailTool: Tool = {
  name: "get_email",
  description: "Retrieve details of a specific email",
  inputSchema: {
    type: "object",
    properties: {
      messageId: {
        type: "string",
        description: "Gmail message ID",
      },
    },
    required: ["messageId"],
  },
  handler: async (client, args) => {
    try {
      const email = await client.getEmail(args.messageId);

      // Extract relevant info
      const headers = email.payload?.headers || [];
      const subject = headers.find((h: any) => h.name === "Subject")?.value || "No Subject";
      const from = headers.find((h: any) => h.name === "From")?.value || "Unknown";
      const date = headers.find((h: any) => h.name === "Date")?.value || "";

      return `Email Details:\n\nFrom: ${from}\nSubject: ${subject}\nDate: ${date}\n\nSnippet: ${email.snippet || "No preview"}`;
    } catch (error) {
      throw new Error(`Failed to get email: ${error}`);
    }
  },
};

/**
 * Search emails
 */
const searchEmailsTool: Tool = {
  name: "search_emails",
  description: "Search for emails matching a query",
  inputSchema: {
    type: "object",
    properties: {
      query: {
        type: "string",
        description: "Gmail search query (e.g., 'from:john@example.com', 'subject:invoice')",
      },
      maxResults: {
        type: "number",
        description: "Maximum number of results (default: 10)",
      },
    },
    required: ["query"],
  },
  handler: async (client, args) => {
    try {
      const emails = await client.searchEmails(
        args.query,
        args.maxResults || 10
      );

      if (!emails || emails.length === 0) {
        return `No emails found matching query: ${args.query}`;
      }

      let result = `Found ${emails.length} emails:\n\n`;

      for (const email of emails) {
        result += `• ${email.id}\n`;
      }

      return result;
    } catch (error) {
      throw new Error(`Failed to search emails: ${error}`);
    }
  },
};

/**
 * Get unread important emails
 */
const getUnreadImportantTool: Tool = {
  name: "get_unread_important",
  description: "Get all unread important emails",
  inputSchema: {
    type: "object",
    properties: {
      maxResults: {
        type: "number",
        description: "Maximum number of results (default: 20)",
      },
    },
    required: [],
  },
  handler: async (client, args) => {
    try {
      const emails = await client.getUnreadImportant(args.maxResults || 20);

      if (!emails || emails.length === 0) {
        return "✓ No unread important emails";
      }

      let result = `Unread Important Emails (${emails.length}):\n\n`;

      for (const email of emails) {
        result += `• ${email.id}\n`;
      }

      result += "\nUse get_email to retrieve details of any message.";

      return result;
    } catch (error) {
      throw new Error(`Failed to get unread emails: ${error}`);
    }
  },
};

/**
 * Export all tools
 */
export const tools: Tool[] = [
  sendEmailTool,
  createDraftTool,
  getEmailTool,
  searchEmailsTool,
  getUnreadImportantTool,
];
