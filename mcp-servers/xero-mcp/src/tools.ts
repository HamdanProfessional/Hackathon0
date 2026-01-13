/**
 * MCP Tools Definitions
 *
 * Defines all available tools for the Xero MCP server.
 */

import { XeroClient } from "./xero-client.js";

export interface Tool {
  name: string;
  description: string;
  inputSchema: any;
  handler: (client: XeroClient, args: any) => Promise<string>;
}

/**
 * Create a new invoice in Xero
 */
const createInvoiceTool: Tool = {
  name: "create_invoice",
  description:
    "Create a new invoice in Xero. Requires contact ID, line items, and optionally due date and reference.",
  inputSchema: {
    type: "object",
    properties: {
      contactId: {
        type: "string",
        description: "Xero contact ID for the customer",
      },
      lineItems: {
        type: "array",
        description: "Line items for the invoice",
        items: {
          type: "object",
          properties: {
            description: {
              type: "string",
              description: "Description of the line item",
            },
            quantity: {
              type: "number",
              description: "Quantity of items",
            },
            unitAmount: {
              type: "number",
              description: "Unit price in currency",
            },
            accountCode: {
              type: "string",
              description: "Xero account code (e.g., '200' for Sales)",
            },
          },
          required: ["description", "quantity", "unitAmount", "accountCode"],
        },
      },
      dueDate: {
        type: "string",
        description: "Due date in YYYY-MM-DD format (optional)",
      },
      reference: {
        type: "string",
        description: "Reference number for the invoice (optional)",
      },
    },
    required: ["contactId", "lineItems"],
  },
  handler: async (client, args) => {
    try {
      const invoiceId = await client.createInvoice({
        contactId: args.contactId,
        lineItems: args.lineItems,
        dueDate: args.dueDate,
        reference: args.reference,
      });

      return `✓ Invoice created successfully\nInvoice ID: ${invoiceId}\n\nNote: Invoice is in DRAFT status. Use send_invoice to send it to the customer.`;
    } catch (error) {
      throw new Error(`Failed to create invoice: ${error}`);
    }
  },
};

/**
 * Send an invoice to customer
 */
const sendInvoiceTool: Tool = {
  name: "send_invoice",
  description: "Send an invoice to the customer via email. Invoice must exist in Xero first.",
  inputSchema: {
    type: "object",
    properties: {
      invoiceId: {
        type: "string",
        description: "Xero invoice ID to send",
      },
    },
    required: ["invoiceId"],
  },
  handler: async (client, args) => {
    try {
      await client.sendInvoice(args.invoiceId);
      return `✓ Invoice sent to customer\nInvoice ID: ${args.invoiceId}`;
    } catch (error) {
      throw new Error(`Failed to send invoice: ${error}`);
    }
  },
};

/**
 * Get invoice details
 */
const getInvoiceTool: Tool = {
  name: "get_invoice",
  description: "Retrieve details of a specific invoice from Xero",
  inputSchema: {
    type: "object",
    properties: {
      invoiceId: {
        type: "string",
        description: "Xero invoice ID",
      },
    },
    required: ["invoiceId"],
  },
  handler: async (client, args) => {
    try {
      const invoice = await client.getInvoice(args.invoiceId);

      if (!invoice) {
        return `Invoice not found: ${args.invoiceId}`;
      }

      // Format invoice details
      return `Invoice Details:\n${JSON.stringify(invoice, null, 2)}`;
    } catch (error) {
      throw new Error(`Failed to get invoice: ${error}`);
    }
  },
};

/**
 * Create or update a contact
 */
const createContactTool: Tool = {
  name: "create_contact",
  description: "Create a new contact or update an existing one in Xero",
  inputSchema: {
    type: "object",
    properties: {
      name: {
        type: "string",
        description: "Contact name (person or organization)",
      },
      email: {
        type: "string",
        description: "Email address (optional)",
      },
      phoneNumber: {
        type: "string",
        description: "Phone number (optional)",
      },
      address: {
        type: "object",
        description: "Postal address (optional)",
        properties: {
          line1: { type: "string" },
          city: { type: "string" },
          region: { type: "string" },
          postalCode: { type: "string" },
          country: { type: "string" },
        },
      },
    },
    required: ["name"],
  },
  handler: async (client, args) => {
    try {
      const contactId = await client.upsertContact({
        name: args.name,
        email: args.email,
        phoneNumber: args.phoneNumber,
        address: args.address,
      });

      return `✓ Contact created/updated\nContact ID: ${contactId}\nName: ${args.name}`;
    } catch (error) {
      throw new Error(`Failed to create contact: ${error}`);
    }
  },
};

/**
 * Get profit and loss report
 */
const getProfitAndLossTool: Tool = {
  name: "get_profit_loss",
  description: "Retrieve the Profit and Loss statement from Xero",
  inputSchema: {
    type: "object",
    properties: {
      period: {
        type: "string",
        description: "Reporting period (e.g., 'MONTH', 'QUARTER', 'YEAR')",
        enum: ["MONTH", "QUARTER", "YEAR"],
      },
    },
    required: [],
  },
  handler: async (client, args) => {
    try {
      const report = await client.getProfitAndLoss();

      if (!report) {
        return "No Profit and Loss data available";
      }

      // Format report
      const reportRows = report.Rows?.map((row: any) => {
        const cells = row.Cells?.map((cell: any) => cell.Value).join(" | ");
        return cells;
      }).join("\n") || "";

      return `Profit and Loss Statement:\n\n${reportRows}`;
    } catch (error) {
      throw new Error(`Failed to get Profit and Loss: ${error}`);
    }
  },
};

/**
 * Get overdue invoices
 */
const getOverdueInvoicesTool: Tool = {
  name: "get_overdue_invoices",
  description: "Get all overdue invoices that need follow-up",
  inputSchema: {
    type: "object",
    properties: {},
    required: [],
  },
  handler: async (client, args) => {
    try {
      const invoices = await client.getOverdueInvoices();

      if (!invoices || invoices.length === 0) {
        return "✓ No overdue invoices found";
      }

      let result = `Overdue Invoices (${invoices.length}):\n\n`;

      invoices.forEach((invoice: any) => {
        result += `• ${invoice.InvoiceNumber || "No Number"}\n`;
        result += `  Contact: ${invoice.Contact?.Name || "Unknown"}\n`;
        result += `  Amount: ${invoice.Total || 0}\n`;
        result += `  Due: ${invoice.DueDateString || "Unknown"}\n`;
        result += `  Days Overdue: ${invoice.DaysOverdue || 0}\n\n`;
      });

      return result;
    } catch (error) {
      throw new Error(`Failed to get overdue invoices: ${error}`);
    }
  },
};

/**
 * Export all tools
 */
export const tools: Tool[] = [
  createInvoiceTool,
  sendInvoiceTool,
  getInvoiceTool,
  createContactTool,
  getProfitAndLossTool,
  getOverdueInvoicesTool,
];
