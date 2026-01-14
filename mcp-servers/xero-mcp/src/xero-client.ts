/**
 * Xero Client Wrapper
 *
 * Handles authentication and API calls to Xero.
 */

import { XeroClient as XeroSDK, Invoice, Contact, LineItem } from "xero-node";
import { readFileSync, writeFileSync, existsSync } from "fs";
import { join } from "path";

export interface XeroConfig {
  clientId: string;
  clientSecret: string;
  redirectUri: string;
  scopes: string[];
}

export interface TokenData {
  access_token: string;
  refresh_token: string;
  expires_at: string;
  tenantId?: string;
}

export class XeroClient {
  private config: XeroConfig;
  private xero: XeroSDK;
  private tokenPath: string;
  private tenantId: string | null = null;

  constructor(config: XeroConfig) {
    this.config = config;
    this.tokenPath = join(process.cwd(), ".xero_mcp_token.json");

    this.xero = new XeroSDK({
      clientId: config.clientId,
      clientSecret: config.clientSecret,
      redirectUris: [config.redirectUri],
      scopes: config.scopes as any,
    });

    this.loadTenantId();
  }

  /**
   * Check if client is authenticated
   */
  isAuthenticated(): boolean {
    return existsSync(this.tokenPath) && this.tenantId !== null;
  }

  /**
   * Load token from file
   */
  async loadToken(): Promise<void> {
    if (!existsSync(this.tokenPath)) {
      throw new Error("Token file not found. Please authenticate first.");
    }

    const tokenData: TokenData = JSON.parse(readFileSync(this.tokenPath, "utf-8"));

    // Set token directly on the Xero client's internal token set
    await this.xero.setTokenSet({
      access_token: tokenData.access_token,
      refresh_token: tokenData.refresh_token,
      expires_at: new Date(tokenData.expires_at),
    } as any);

    this.tenantId = tokenData.tenantId || null;
  }

  /**
   * Save token to file
   */
  private saveToken(token: any): void {
    const tokenData: TokenData = {
      access_token: token.access_token,
      refresh_token: token.refresh_token,
      expires_at: token.expires_at.toISOString(),
      tenantId: this.tenantId || undefined,
    };

    writeFileSync(this.tokenPath, JSON.stringify(tokenData, null, 2));
  }

  /**
   * Load tenant ID from token file
   */
  private loadTenantId(): void {
    if (existsSync(this.tokenPath)) {
      const tokenData: TokenData = JSON.parse(readFileSync(this.tokenPath, "utf-8"));
      this.tenantId = tokenData.tenantId || null;
    }
  }

  /**
   * Get tenant ID
   */
  getTenantId(): string | null {
    return this.tenantId;
  }

  /**
   * Set tenant ID
   */
  setTenantId(tenantId: string): void {
    this.tenantId = tenantId;
  }

  /**
   * Refresh token if expired
   */
  async refreshAccessToken(): Promise<void> {
    const tokenSet = await this.xero.readTokenSet();

    if (tokenSet.expired()) {
      await this.xero.refreshToken();
      this.saveToken(await this.xero.readTokenSet());
    }
  }

  /**
   * Get Xero SDK instance
   */
  getXero(): XeroSDK {
    return this.xero;
  }

  /**
   * Create invoice
   */
  async createInvoice(invoiceData: {
    contactId: string;
    lineItems: Array<{
      description: string;
      quantity: number;
      unitAmount: number;
      accountCode: string;
    }>;
    dueDate?: string;
    reference?: string;
  }): Promise<string> {
    await this.refreshAccessToken();

    if (!this.tenantId) {
      throw new Error("No tenant ID set");
    }

    const invoice: Invoice = {
      type: "ACCREC" as any,
      status: "DRAFT" as any,
      contact: {
        contactID: invoiceData.contactId,
      },
      lineItems: invoiceData.lineItems.map((item) => ({
        description: item.description,
        quantity: item.quantity,
        unitAmount: item.unitAmount,
        accountCode: item.accountCode,
      })),
      date: new Date().toISOString().split("T")[0],
      dueDate: invoiceData.dueDate || "",
      reference: invoiceData.reference || "",
    };

    const response = await this.xero.accountingApi.createInvoices(
      this.tenantId,
      { invoices: [invoice] }
    );

    const createdInvoice = response.body?.invoices?.[0];
    if (!createdInvoice?.invoiceID) {
      throw new Error("Failed to create invoice");
    }

    return createdInvoice.invoiceID;
  }

  /**
   * Send invoice
   */
  async sendInvoice(invoiceId: string): Promise<void> {
    await this.refreshAccessToken();

    if (!this.tenantId) {
      throw new Error("No tenant ID set");
    }

    // Email invoice - provide all required parameters
    await this.xero.accountingApi.emailInvoice(
      this.tenantId,
      invoiceId,
      {}
    );
  }

  /**
   * Get invoice by ID
   */
  async getInvoice(invoiceId: string): Promise<any> {
    await this.refreshAccessToken();

    if (!this.tenantId) {
      throw new Error("No tenant ID set");
    }

    const response = await this.xero.accountingApi.getInvoice(
      this.tenantId,
      invoiceId
    );

    return response.body?.invoices?.[0];
  }

  /**
   * Create or update contact
   */
  async upsertContact(contactData: {
    name: string;
    email?: string;
    phoneNumber?: string;
    address?: {
      line1?: string;
      city?: string;
      region?: string;
      postalCode?: string;
      country?: string;
    };
  }): Promise<string> {
    await this.refreshAccessToken();

    if (!this.tenantId) {
      throw new Error("No tenant ID set");
    }

    const contact: Contact = {
      name: contactData.name,
      emailAddress: contactData.email,
      phones: contactData.phoneNumber
        ? [{
            phoneNumber: contactData.phoneNumber,
            phoneType: "DEFAULT" as any
          }]
        : undefined,
      addresses: contactData.address
        ? [
            {
              addressType: "STREET" as any,
              addressLine1: contactData.address.line1,
              city: contactData.address.city,
              region: contactData.address.region,
              postalCode: contactData.address.postalCode,
              country: contactData.address.country,
            },
          ]
        : undefined,
    };

    const response = await this.xero.accountingApi.createContacts(
      this.tenantId,
      { contacts: [contact] }
    );

    const createdContact = response.body?.contacts?.[0];
    if (!createdContact?.contactID) {
      throw new Error("Failed to create contact");
    }

    return createdContact.contactID;
  }

  /**
   * Get profit and loss report
   */
  async getProfitAndLoss(): Promise<any> {
    await this.refreshAccessToken();

    if (!this.tenantId) {
      throw new Error("No tenant ID set");
    }

    const response = await this.xero.accountingApi.getReportProfitAndLoss(
      this.tenantId
    );

    return response.body?.reports?.[0];
  }

  /**
   * Get overdue invoices
   */
  async getOverdueInvoices(): Promise<any[]> {
    await this.refreshAccessToken();

    if (!this.tenantId) {
      throw new Error("No tenant ID set");
    }

    // Get all invoices and filter manually (Xero query has issues with date comparisons)
    const response = await this.xero.accountingApi.getInvoices(
      this.tenantId
    );

    const allInvoices = response.body?.invoices || [];
    const today = new Date();

    // Filter for overdue invoices
    return allInvoices.filter((invoice: any) => {
      if (invoice.status === "PAID" || invoice.status === "VOIDED") {
        return false;
      }
      if (!invoice.dueDate) {
        return false;
      }
      const dueDate = new Date(invoice.dueDate);
      return dueDate < today;
    });
  }
}
