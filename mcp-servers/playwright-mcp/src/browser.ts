/**
 * Playwright Browser Management
 *
 * Manages browser connection and page operations.
 * Supports two modes:
 * - CDP mode: Connects to existing Chrome CDP session (local development)
 * - Headless mode: Launches new headless browser (cloud VM)
 */

import { chromium } from 'playwright';

export interface BrowserConfig {
  cdpEndpoint?: string;
  headless?: boolean;
  timeout?: number;
  useCDP?: boolean;  // If false, use headless mode (for cloud VM)
}

export class BrowserManager {
  private browser: any = null;
  private context: any = null;
  private page: any = null;
  public config: BrowserConfig;

  constructor(config: BrowserConfig = {}) {
    this.config = {
      cdpEndpoint: config.cdpEndpoint || 'http://localhost:9222',
      headless: config.headless ?? true,
      timeout: config.timeout ?? 30000,
      useCDP: config.useCDP ?? false,  // Default to headless for cloud VM
    };
  }

  async connect(): Promise<string> {
    /**
     * Connect to browser:
     * - CDP mode: Reuses existing Chrome session (local dev)
     * - Headless mode: Launches new headless browser (cloud VM)
     */
    if (this.config.useCDP) {
      return this._connectCDP();
    } else {
      return this._connectHeadless();
    }
  }

  private async _connectCDP(): Promise<string> {
    /** Connect to Chrome via CDP (local development mode) */
    try {
      this.browser = await chromium.connectOverCDP(
        this.config.cdpEndpoint as string,
        {}  // Use default options
      );

      // Get the first context and page
      const contexts = this.browser.contexts();
      if (contexts.length === 0) {
        throw new Error('No browser contexts available');
      }

      this.context = contexts[0];
      this.page = await this.context.newPage();

      // Set default timeout
      this.page.setDefaultTimeout(this.config.timeout);

      return `Connected to Chrome via CDP (${this.config.cdpEndpoint})`;
    } catch (error) {
      throw new Error(`Failed to connect to Chrome CDP: ${error}`);
    }
  }

  private async _connectHeadless(): Promise<string> {
    /** Launch headless browser (cloud VM mode) */
    try {
      this.browser = await chromium.launch({
        headless: this.config.headless ?? true,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-gpu'
        ]
      });

      // Create context and page
      this.context = await this.browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      });

      this.page = await this.context.newPage();

      // Set default timeout
      this.page.setDefaultTimeout(this.config.timeout);

      return `Launched headless Chrome (headless=${this.config.headless})`;
    } catch (error) {
      throw new Error(`Failed to launch headless browser: ${error}`);
    }
  }

  async disconnect(): Promise<void> {
    if (this.page) {
      await this.page.close();
    }
    if (this.context) {
      await this.context.close();
    }
    if (this.browser) {
      await this.browser.close();
    }
    this.page = null;
    this.context = null;
    this.browser = null;
  }

  async getPage(): Promise<any> {
    /** Get or create the active page. */
    if (!this.page) {
      await this.connect();
    }
    return this.page;
  }

  isConnected(): boolean {
    return this.browser !== null;
  }

  async getCurrentPage(): Promise<any> {
    if (!this.page) {
      await this.connect();
    }
    return this.page;
  }
}
