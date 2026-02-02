/**
 * MCP Tool Definitions for WhatsApp
 */

import { WhatsAppClient } from "./whatsapp-client.js";

export interface Tool {
  name: string;
  description: string;
  inputSchema: {
    type: "object";
    properties: Record<string, {
      type: string;
      description: string;
    }>;
    required?: string[];
  };
  handler: (client: WhatsAppClient, args: any) => Promise<string>;
}

export const tools: Tool[] = [
  {
    name: "send_message",
    description: "Send a message to a WhatsApp contact or group",
    inputSchema: {
      type: "object",
      properties: {
        contact: {
          type: "string",
          description: "Contact name or phone number to send message to",
        },
        message: {
          type: "string",
          description: "Message text to send",
        },
      },
      required: ["contact", "message"],
    },
    handler: async (client, args) => {
      const result = await client.sendMessage({
        contact: args.contact,
        message: args.message,
      });

      return result;
    },
  },

  {
    name: "get_chats",
    description: "Get list of recent WhatsApp chats",
    inputSchema: {
      type: "object",
      properties: {
        limit: {
          type: "string",
          description: "Maximum number of chats to retrieve (default: 20)",
        },
      },
    },
    handler: async (client, args) => {
      const limit = args.limit ? parseInt(args.limit) : 20;
      const chats = await client.getChats(limit);

      if (chats.length === 0) {
        return "No chats found.";
      }

      const chatList = chats
        .map((chat) => {
          const unread = chat.unreadCount && chat.unreadCount > 0
            ? ` (${chat.unreadCount} unread)`
            : "";
          const lastMsg = chat.lastMessage
            ? `\n  Last: ${chat.lastMessage.substring(0, 50)}${chat.lastMessage.length > 50 ? "..." : ""}`
            : "";
          return `- ${chat.name}${unread}${lastMsg}`;
        })
        .join("\n");

      return `Found ${chats.length} chats:\n\n${chatList}`;
    },
  },

  {
    name: "get_messages",
    description: "Get recent messages from a specific chat",
    inputSchema: {
      type: "object",
      properties: {
        contact: {
          type: "string",
          description: "Contact name to get messages from",
        },
        limit: {
          type: "string",
          description: "Number of messages to retrieve (default: 10)",
        },
      },
      required: ["contact"],
    },
    handler: async (client, args) => {
      const limit = args.limit ? parseInt(args.limit) : 10;
      const messages = await client.getMessages(args.contact, limit);

      if (messages.length === 0) {
        return `No messages found in chat with ${args.contact}.`;
      }

      const messageList = messages
        .map((msg) => `**${msg.from}**: ${msg.text}`)
        .join("\n\n");

      return `Recent messages from ${args.contact}:\n\n${messageList}`;
    },
  },

  {
    name: "check_status",
    description: "Check WhatsApp connection status",
    inputSchema: {
      type: "object",
      properties: {},
    },
    handler: async (client) => {
      const isConnected = client.getConnectedStatus();

      return isConnected
        ? "✓ WhatsApp is connected and ready"
        : "⚠ WhatsApp is not connected. Please authenticate first.";
    },
  },
];
