/**
 * Slack Client Wrapper
 *
 * Handles API calls to Slack for sending messages and managing channels.
 */

import { WebClient } from "@slack/web-api";

export interface SlackConfig {
  botToken: string;
}

export class SlackClient {
  private client: WebClient;
  private botUserId: string | null = null;

  constructor(config: SlackConfig) {
    this.client = new WebClient(config.botToken);
  }

  /**
   * Check if client is authenticated
   */
  async isAuthenticated(): Promise<boolean> {
    try {
      const authInfo = await this.client.auth.test();
      this.botUserId = authInfo.user_id as string;
      return true;
    } catch (error) {
      console.error("Slack authentication failed:", error);
      return false;
    }
  }

  /**
   * Send message to a channel
   */
  async sendMessage(params: {
    channel: string;
    text: string;
    threadTs?: string;
  }): Promise<string> {
    try {
      const result = await this.client.chat.postMessage({
        channel: params.channel,
        text: params.text,
        thread_ts: params.threadTs,
      });

      return result.ts as string;
    } catch (error) {
      throw new Error(`Failed to send message: ${error}`);
    }
  }

  /**
   * Get channel list
   */
  async getChannels(): Promise<any[]> {
    try {
      const result = await this.client.conversations.list({
        types: "public_channel,private_channel",
      });

      return result.channels as any[];
    } catch (error) {
      throw new Error(`Failed to get channels: ${error}`);
    }
  }

  /**
   * Get channel information
   */
  async getChannelInfo(channelId: string): Promise<any> {
    try {
      const result = await this.client.conversations.info({
        channel: channelId,
      });

      return result.channel as any;
    } catch (error) {
      throw new Error(`Failed to get channel info: ${error}`);
    }
  }

  /**
   * Get messages from a channel
   */
  async getMessages(channelId: string, limit: number = 10): Promise<any[]> {
    try {
      const result = await this.client.conversations.history({
        channel: channelId,
        limit,
      });

      return result.messages as any[];
    } catch (error) {
      throw new Error(`Failed to get messages: ${error}`);
    }
  }

  /**
   * Get user information
   */
  async getUserInfo(userId: string): Promise<any> {
    try {
      const result = await this.client.users.info({
        user: userId,
      });

      return result.user as any;
    } catch (error) {
      throw new Error(`Failed to get user info: ${error}`);
    }
  }

  /**
   * Get bot user ID
   */
  getBotUserId(): string | null {
    return this.botUserId;
  }
}
