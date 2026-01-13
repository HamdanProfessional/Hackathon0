/**
 * Email Client Wrapper
 *
 * Handles authentication and API calls to Gmail.
 */

import { google } from "googleapis";
import { readFileSync, writeFileSync, existsSync } from "fs";
import { join } from "path";
import { OAuth2Client } from "google-auth-library";

export interface EmailConfig {
  credentialsPath: string;
  tokenPath: string;
}

export class EmailClient {
  private config: EmailConfig;
  private gmail: any;
  private oauth2Client: OAuth2Client;

  constructor(config: EmailConfig) {
    this.config = config;
    this.oauth2Client = new OAuth2Client({
      clientId: "",
      clientSecret: "",
      redirectUri: "urn:ietf:wg:oauth:2.0:oob",
    });
  }

  /**
   * Check if client is authenticated
   */
  isAuthenticated(): boolean {
    return existsSync(this.config.tokenPath);
  }

  /**
   * Load token from file
   */
  async loadToken(): Promise<void> {
    if (!existsSync(this.config.tokenPath)) {
      throw new Error("Token file not found. Please authenticate first.");
    }

    const token = JSON.parse(readFileSync(this.config.tokenPath, "utf-8"));

    this.oauth2Client.setCredentials(token);
    this.gmail = google.gmail({ version: "v1", auth: this.oauth2Client });
  }

  /**
   * Save token to file
   */
  private saveToken(): void {
    const credentials = this.oauth2Client.credentials;
    writeFileSync(this.config.tokenPath, JSON.stringify(credentials, null, 2));
  }

  /**
   * Send email
   */
  async sendEmail(params: {
    to: string;
    subject: string;
    body: string;
    cc?: string;
    bcc?: string;
  }): Promise<string> {
    await this.loadToken();

    // Encode message
    const email = [
      `To: ${params.to}`,
      params.cc ? `Cc: ${params.cc}` : "",
      params.bcc ? `Bcc: ${params.bcc}` : "",
      `Subject: ${params.subject}`,
      "",
      params.body,
    ].join("\r\n");

    const encodedMessage = Buffer.from(email)
      .toString("base64")
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/, "");

    const response = await this.gmail.users.messages.send({
      userId: "me",
      requestBody: {
        raw: encodedMessage,
      },
    });

    return response.data.id;
  }

  /**
   * Create draft email
   */
  async createDraft(params: {
    to: string;
    subject: string;
    body: string;
    cc?: string;
    bcc?: string;
  }): Promise<string> {
    await this.loadToken();

    // Encode message
    const email = [
      `To: ${params.to}`,
      params.cc ? `Cc: ${params.cc}` : "",
      params.bcc ? `Bcc: ${params.bcc}` : "",
      `Subject: ${params.subject}`,
      "",
      params.body,
    ].join("\r\n");

    const encodedMessage = Buffer.from(email)
      .toString("base64")
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/, "");

    const response = await this.gmail.users.drafts.create({
      userId: "me",
      requestBody: {
        message: {
          raw: encodedMessage,
        },
      },
    });

    return response.data.id;
  }

  /**
   * Get email by ID
   */
  async getEmail(messageId: string): Promise<any> {
    await this.loadToken();

    const response = await this.gmail.users.messages.get({
      userId: "me",
      id: messageId,
      format: "full",
    });

    return response.data;
  }

  /**
   * Search emails
   */
  async searchEmails(query: string, maxResults: number = 10): Promise<any[]> {
    await this.loadToken();

    const response = await this.gmail.users.messages.list({
      userId: "me",
      q: query,
      maxResults: maxResults,
    });

    return response.data.messages || [];
  }

  /**
   * Get unread important emails
   */
  async getUnreadImportant(maxResults: number = 20): Promise<any[]> {
    return this.searchEmails("is:unread is:important", maxResults);
  }
}
