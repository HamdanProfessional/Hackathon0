/**
 * Calendar Client Wrapper
 *
 * Handles authentication and API calls to Google Calendar.
 */

import { google } from "googleapis";
import { OAuth2Client } from "google-auth-library";
import { readFileSync, writeFileSync, existsSync } from "fs";

export interface CalendarConfig {
  credentialsPath: string;
  tokenPath: string;
}

export class CalendarClient {
  private config: CalendarConfig;
  private calendar: any;
  private oauth2Client: OAuth2Client;

  constructor(config: CalendarConfig) {
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
    this.calendar = google.calendar({ version: "v3", auth: this.oauth2Client });
  }

  /**
   * Create calendar event
   */
  async createEvent(params: {
    summary: string;
    description?: string;
    startTime: string;
    endTime: string;
    attendees?: string[];
    location?: string;
  }): Promise<string> {
    await this.loadToken();

    const event = {
      summary: params.summary,
      description: params.description,
      location: params.location,
      start: {
        dateTime: params.startTime,
      },
      end: {
        dateTime: params.endTime,
      },
      attendees: params.attendees?.map(email => ({ email })),
    };

    const response = await this.calendar.events.insert({
      calendarId: "primary",
      requestBody: event,
      sendUpdates: "none", // Don't send invitations yet
    });

    return response.data.id;
  }

  /**
   * Get event by ID
   */
  async getEvent(eventId: string): Promise<any> {
    await this.loadToken();

    const response = await this.calendar.events.get({
      calendarId: "primary",
      eventId: eventId,
    });

    return response.data;
  }

  /**
   * List events in a time range
   */
  async listEvents(timeMin: string, timeMax: string, maxResults: number = 10): Promise<any[]> {
    await this.loadToken();

    const response = await this.calendar.events.list({
      calendarId: "primary",
      timeMin: timeMin,
      timeMax: timeMax,
      maxResults: maxResults,
      singleEvents: true,
      orderBy: "startTime",
    });

    return response.data.items || [];
  }

  /**
   * Update event
   */
  async updateEvent(eventId: string, updates: any): Promise<void> {
    await this.loadToken();

    await this.calendar.events.update({
      calendarId: "primary",
      eventId: eventId,
      requestBody: updates,
    });
  }

  /**
   * Delete event
   */
  async deleteEvent(eventId: string): Promise<void> {
    await this.loadToken();

    await this.calendar.events.delete({
      calendarId: "primary",
      eventId: eventId,
    });
  }

  /**
   * Get upcoming events
   */
  async getUpcomingEvents(hours: number = 24): Promise<any[]> {
    const now = new Date();
    const timeMax = new Date(now.getTime() + hours * 60 * 60 * 1000);

    return this.listEvents(
      now.toISOString(),
      timeMax.toISOString(),
      20
    );
  }
}
