/**
 * WhatsApp Client Wrapper
 *
 * Handles WhatsApp Web automation via Playwright for sending messages
 * and managing WhatsApp communications.
 */

import { chromium, Browser, BrowserContext, Page } from "playwright";

export interface WhatsAppConfig {
  sessionPath?: string;
  headless?: boolean;
}

export interface ChatInfo {
  id: string;
  name: string;
  lastMessage?: string;
  timestamp?: string;
  unreadCount?: number;
}

export interface MessageInfo {
  id: string;
  text: string;
  from: string;
  timestamp: string;
}

export class WhatsAppClient {
  private browser: Browser | null = null;
  private context: BrowserContext | null = null;
  private page: Page | null = null;
  private sessionPath: string;
  private headless: boolean;
  private isAuthenticated: boolean = false;

  constructor(config: WhatsAppConfig = {}) {
    this.sessionPath = config.sessionPath || "./whatsapp_mcp_session";
    this.headless = config.headless ?? false;
  }

  /**
   * Initialize browser and connect to WhatsApp Web
   */
  async connect(): Promise<boolean> {
    try {
      console.error("Connecting to WhatsApp Web...");

      // Launch browser with persistent context
      this.browser = await chromium.launch({
        headless: this.headless,
      });

      this.context = await this.browser.newContext({
        viewport: { width: 1280, height: 800 },
        userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      });

      // Load session storage if exists
      try {
        if (this.context) {
          await this.context.storageState({ path: `${this.sessionPath}/storage-state.json` });
        }
      } catch {
        // No saved session, will need QR code scan
      }

      if (!this.context) {
        throw new Error("Failed to create browser context");
      }

      this.page = await this.context.newPage();

      // Navigate to WhatsApp Web
      await this.page.goto("https://web.whatsapp.com", {
        waitUntil: "networkidle",
        timeout: 60000,
      });

      // Wait for either login (QR code) or main interface
      await this.page.waitForTimeout(3000);

      // Check if already logged in
      const isLoggedIn = await this.checkLoginStatus();

      if (!isLoggedIn) {
        console.error("⚠ WhatsApp not authenticated. Please scan QR code.");
        // Wait for user to scan QR code (up to 2 minutes)
        await this.waitForLogin();
      }

      // Save session state for next time
      await this.context.storageState({ path: `${this.sessionPath}/storage-state.json` });

      this.isAuthenticated = true;
      console.error("✓ WhatsApp authenticated");
      return true;
    } catch (error) {
      console.error("Failed to connect to WhatsApp:", error);
      return false;
    }
  }

  /**
   * Check if user is logged in
   */
  private async checkLoginStatus(): Promise<boolean> {
    if (!this.page) return false;

    try {
      // Check for main interface elements
      const selectors = [
        '[data-testid="chat-list"]',
        '#side',
        '[data-testid="pane-side"]',
      ];

      for (const selector of selectors) {
        const element = await this.page.$(selector);
        if (element) {
          return true;
        }
      }

      return false;
    } catch {
      return false;
    }
  }

  /**
   * Wait for user to scan QR code and log in
   */
  private async waitForLogin(timeout: number = 120000): Promise<boolean> {
    if (!this.page) return false;

    try {
      await this.page.waitForSelector('[data-testid="chat-list"], #side, [data-testid="pane-side"]', {
        timeout,
      });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Send a message to a contact or group
   */
  async sendMessage(params: {
    contact: string;
    message: string;
  }): Promise<string> {
    if (!this.page || !this.isAuthenticated) {
      throw new Error("WhatsApp not connected. Call connect() first.");
    }

    try {
      const { contact, message } = params;

      // Search for contact
      await this.page.click('[data-testid="chat-list-search"]');
      await this.page.fill('[data-testid="chat-list-search"]', contact);
      await this.page.waitForTimeout(1000);

      // Click on the contact
      const contactSelector = `[data-testid="cell-frame-container"] >> text=${contact}`;
      await this.page.click(contactSelector, { timeout: 10000 });
      await this.page.waitForTimeout(1000);

      // Type message
      await this.page.fill('[data-testid="conversation-panel-footer"] >> div[contenteditable="true"]', message);

      // Send message
      await this.page.click('[data-testid="send-button"]');

      // Wait for message to be sent
      await this.page.waitForTimeout(1000);

      return `Message sent to ${contact}`;
    } catch (error) {
      throw new Error(`Failed to send message: ${error}`);
    }
  }

  /**
   * Get list of chats
   */
  async getChats(limit: number = 20): Promise<ChatInfo[]> {
    if (!this.page || !this.isAuthenticated) {
      throw new Error("WhatsApp not connected. Call connect() first.");
    }

    try {
      const chats: ChatInfo[] = [];

      // Wait for chat list to load
      await this.page.waitForSelector('[data-testid="chat-list"]', { timeout: 10000 });

      // Get chat elements
      const chatElements = await this.page.$$('[data-testid="chat-container"]');

      for (let i = 0; i < Math.min(chatElements.length, limit); i++) {
        try {
          const chat = chatElements[i];

          // Get chat name
          const nameElement = await chat.$('[data-testid="conversation-title"]');
          const name = await nameElement?.textContent() || "Unknown";

          // Get last message preview
          const lastMessageElement = await chat.$('[data-testid="last-message"]');
          const lastMessage = await lastMessageElement?.textContent() || "";

          // Get unread count if available
          const unreadElement = await chat.$('[data-testid="unread-count"]');
          const unreadText = await unreadElement?.textContent() || "0";
          const unreadCount = parseInt(unreadText) || 0;

          chats.push({
            id: `chat_${i}`,
            name: name.trim(),
            lastMessage: lastMessage.trim(),
            unreadCount,
          });
        } catch {
          continue;
        }
      }

      return chats;
    } catch (error) {
      throw new Error(`Failed to get chats: ${error}`);
    }
  }

  /**
   * Get recent messages from a chat
   */
  async getMessages(contact: string, limit: number = 10): Promise<MessageInfo[]> {
    if (!this.page || !this.isAuthenticated) {
      throw new Error("WhatsApp not connected. Call connect() first.");
    }

    try {
      // Search and open chat
      await this.page.click('[data-testid="chat-list-search"]');
      await this.page.fill('[data-testid="chat-list-search"]', contact);
      await this.page.waitForTimeout(1000);

      const contactSelector = `[data-testid="cell-frame-container"] >> text=${contact}`;
      await this.page.click(contactSelector, { timeout: 10000 });
      await this.page.waitForTimeout(1500);

      const messages: MessageInfo[] = [];

      // Get message elements
      const messageElements = await this.page.$$('[data-testid="msg-container"]');

      for (let i = 0; i < Math.min(messageElements.length, limit); i++) {
        try {
          const msg = messageElements[i];

          // Get message text
          const textElement = await msg.$('.selectable-text >> span');
          const text = await textElement?.textContent() || "";

          // Get sender info
          const fromElement = await msg.$('[data-testid="msg-meta"]');
          const from = await fromElement?.textContent() || "";

          messages.push({
            id: `msg_${i}`,
            text: text.trim(),
            from: from.trim(),
            timestamp: new Date().toISOString(),
          });
        } catch {
          continue;
        }
      }

      return messages.reverse();
    } catch (error) {
      throw new Error(`Failed to get messages: ${error}`);
    }
  }

  /**
   * Check authentication status
   */
  getConnectedStatus(): boolean {
    return this.isAuthenticated;
  }

  /**
   * Close browser and cleanup
   */
  async close(): Promise<void> {
    if (this.context) {
      await this.context.storageState({ path: `${this.sessionPath}/storage-state.json` });
    }
    if (this.page) await this.page.close();
    if (this.context) await this.context.close();
    if (this.browser) await this.browser.close();

    this.page = null;
    this.context = null;
    this.browser = null;
    this.isAuthenticated = false;
  }
}
