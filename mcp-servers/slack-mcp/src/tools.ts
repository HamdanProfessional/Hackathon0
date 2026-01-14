/**
 * MCP Tool Definitions for Slack
 */

import { SlackClient } from "./slack-client.js";

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
  handler: (client: SlackClient, args: any) => Promise<string>;
}

export const tools: Tool[] = [
  {
    name: "send_message",
    description: "Send a message to a Slack channel or DM",
    inputSchema: {
      type: "object",
      properties: {
        channel: {
          type: "string",
          description: "Channel ID, name (e.g., #general), or user ID for DM",
        },
        text: {
          type: "string",
          description: "Message text to send",
        },
        thread_ts: {
          type: "string",
          description: "Optional: Thread timestamp to reply in a thread",
        },
      },
      required: ["channel", "text"],
    },
    handler: async (client, args) => {
      const messageTs = await client.sendMessage({
        channel: args.channel,
        text: args.text,
        threadTs: args.thread_ts,
      });

      return `Message sent successfully. Timestamp: ${messageTs}`;
    },
  },

  {
    name: "get_channels",
    description: "Get list of all public and private channels",
    inputSchema: {
      type: "object",
      properties: {},
    },
    handler: async (client) => {
      const channels = await client.getChannels();

      const channelList = channels
        .map((ch) => `- ${ch.name} (${ch.id}): ${ch.topic?.value || "No topic"}`)
        .join("\n");

      return `Found ${channels.length} channels:\n\n${channelList}`;
    },
  },

  {
    name: "get_channel_info",
    description: "Get detailed information about a specific channel",
    inputSchema: {
      type: "object",
      properties: {
        channel_id: {
          type: "string",
          description: "Channel ID to get information for",
        },
      },
      required: ["channel_id"],
    },
    handler: async (client, args) => {
      const channel = await client.getChannelInfo(args.channel_id);

      return `Channel: ${channel.name}
ID: ${channel.id}
Topic: ${channel.topic?.value || "No topic"}
Purpose: ${channel.purpose?.value || "No purpose"}
Members: ${channel.num_members || "Unknown"}
Private: ${channel.is_private || false}`;
    },
  },

  {
    name: "get_messages",
    description: "Get recent messages from a channel",
    inputSchema: {
      type: "object",
      properties: {
        channel_id: {
          type: "string",
          description: "Channel ID to get messages from",
        },
        limit: {
          type: "string",
          description: "Number of messages to retrieve (default: 10)",
        },
      },
      required: ["channel_id"],
    },
    handler: async (client, args) => {
      const limit = args.limit ? parseInt(args.limit) : 10;
      const messages = await client.getMessages(args.channel_id, limit);

      if (messages.length === 0) {
        return "No messages found in this channel.";
      }

      const messageList = await Promise.all(
        messages.map(async (msg) => {
          if (!msg.user) return msg.text || "No text";

          try {
            const user = await client.getUserInfo(msg.user);
            const userName = user.real_name || user.name || "Unknown";
            return `**${userName}**: ${msg.text}`;
          } catch {
            return msg.text || "No text";
          }
        })
      );

      return messageList.reverse().join("\n\n");
    },
  },

  {
    name: "get_user_info",
    description: "Get information about a Slack user",
    inputSchema: {
      type: "object",
      properties: {
        user_id: {
          type: "string",
          description: "User ID to get information for",
        },
      },
      required: ["user_id"],
    },
    handler: async (client, args) => {
      const user = await client.getUserInfo(args.user_id);

      return `Name: ${user.real_name || user.name}
ID: ${user.id}
Email: ${user.profile?.email || "Not set"}
Title: ${user.profile?.title || "Not set"}
Time Zone: ${user.tz || "Unknown"}`;
    },
  },
];
