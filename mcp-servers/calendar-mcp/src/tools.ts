/**
 * MCP Tools Definitions
 *
 * Defines all available tools for the Calendar MCP server.
 */

import { CalendarClient } from "./calendar-client.js";

export interface Tool {
  name: string;
  description: string;
  inputSchema: any;
  handler: (client: CalendarClient, args: any) => Promise<string>;
}

/**
 * Create calendar event
 */
const createEventTool: Tool = {
  name: "create_event",
  description: "Create a new calendar event",
  inputSchema: {
    type: "object",
    properties: {
      summary: {
        type: "string",
        description: "Event title",
      },
      description: {
        type: "string",
        description: "Event description (optional)",
      },
      startTime: {
        type: "string",
        description: "Start time in ISO format (YYYY-MM-DDTHH:MM:SS)",
      },
      endTime: {
        type: "string",
        description: "End time in ISO format (YYYY-MM-DDTHH:MM:SS)",
      },
      attendees: {
        type: "array",
        description: "List of attendee email addresses",
        items: { type: "string" },
      },
      location: {
        type: "string",
        description: "Event location (optional)",
      },
    },
    required: ["summary", "startTime", "endTime"],
  },
  handler: async (client, args) => {
    try {
      const eventId = await client.createEvent({
        summary: args.summary,
        description: args.description,
        startTime: args.startTime,
        endTime: args.endTime,
        attendees: args.attendees,
        location: args.location,
      });

      return `✓ Event created successfully\nEvent ID: ${eventId}\n\nTitle: ${args.summary}\nStart: ${args.startTime}\nEnd: ${args.endTime}\n${args.attendees ? `Attendees: ${args.attendees.join(", ")}\n` : ""}${args.location ? `Location: ${args.location}` : ""}`;
    } catch (error) {
      throw new Error(`Failed to create event: ${error}`);
    }
  },
};

/**
 * Get event details
 */
const getEventTool: Tool = {
  name: "get_event",
  description: "Retrieve details of a specific calendar event",
  inputSchema: {
    type: "object",
    properties: {
      eventId: {
        type: "string",
        description: "Calendar event ID",
      },
    },
    required: ["eventId"],
  },
  handler: async (client, args) => {
    try {
      const event = await client.getEvent(args.eventId);

      return `Event Details:\n\nTitle: ${event.summary}\nDescription: ${event.description || "No description"}\nStart: ${event.start?.dateTime || event.start?.date}\nEnd: ${event.end?.dateTime || event.end?.date}\nLocation: ${event.location || "No location"}\nAttendees: ${event.attendees?.map((a: any) => a.email).join(", ") || "None"}`;
    } catch (error) {
      throw new Error(`Failed to get event: ${error}`);
    }
  },
};

/**
 * List events in time range
 */
const listEventsTool: Tool = {
  name: "list_events",
  description: "List calendar events within a time range",
  inputSchema: {
    type: "object",
    properties: {
      timeMin: {
        type: "string",
        description: "Start of time range (ISO format)",
      },
      timeMax: {
        type: "string",
        description: "End of time range (ISO format)",
      },
      maxResults: {
        type: "number",
        description: "Maximum number of results (default: 10)",
      },
    },
    required: ["timeMin", "timeMax"],
  },
  handler: async (client, args) => {
    try {
      const events = await client.listEvents(
        args.timeMin,
        args.timeMax,
        args.maxResults || 10
      );

      if (!events || events.length === 0) {
        return "No events found in the specified time range.";
      }

      let result = `Found ${events.length} events:\n\n`;

      events.forEach((event: any) => {
        const start = event.start?.dateTime || event.start?.date || "TBD";
        const end = event.end?.dateTime || event.end?.date || "TBD";
        result += `• ${event.summary}\n  ${start} - ${end}\n  ID: ${event.id}\n\n`;
      });

      return result;
    } catch (error) {
      throw new Error(`Failed to list events: ${error}`);
    }
  },
};

/**
 * Get upcoming events
 */
const getUpcomingEventsTool: Tool = {
  name: "get_upcoming_events",
  description: "Get upcoming calendar events (next 24 hours by default)",
  inputSchema: {
    type: "object",
    properties: {
      hours: {
        type: "number",
        description: "Hours ahead to look (default: 24)",
      },
    },
    required: [],
  },
  handler: async (client, args) => {
    try {
      const events = await client.getUpcomingEvents(args.hours || 24);

      if (!events || events.length === 0) {
        return "✓ No upcoming events in the specified time range.";
      }

      let result = `Upcoming Events (${events.length}):\n\n`;

      events.forEach((event: any) => {
        const start = event.start?.dateTime || event.start?.date || "TBD";
        result += `• ${event.summary}\n  ${start}\n  ID: ${event.id}\n\n`;
      });

      return result;
    } catch (error) {
      throw new Error(`Failed to get upcoming events: ${error}`);
    }
  },
};

/**
 * Update event
 */
const updateEventTool: Tool = {
  name: "update_event",
  description: "Update an existing calendar event",
  inputSchema: {
    type: "object",
    properties: {
      eventId: {
        type: "string",
        description: "Calendar event ID to update",
      },
      summary: {
        type: "string",
        description: "New event title",
      },
      description: {
        type: "string",
        description: "New event description",
      },
      location: {
        type: "string",
        description: "New location",
      },
    },
    required: ["eventId"],
  },
  handler: async (client, args) => {
    try {
      const updates: any = {};
      if (args.summary) updates.summary = args.summary;
      if (args.description) updates.description = args.description;
      if (args.location) updates.location = args.location;

      await client.updateEvent(args.eventId, updates);

      return `✓ Event updated successfully\nEvent ID: ${args.eventId}\n\nUpdated fields: ${Object.keys(updates).join(", ")}`;
    } catch (error) {
      throw new Error(`Failed to update event: ${error}`);
    }
  },
};

/**
 * Delete event
 */
const deleteEventTool: Tool = {
  name: "delete_event",
  description: "Delete a calendar event",
  inputSchema: {
    type: "object",
    properties: {
      eventId: {
        type: "string",
        description: "Calendar event ID to delete",
      },
    },
    required: ["eventId"],
  },
  handler: async (client, args) => {
    try {
      await client.deleteEvent(args.eventId);
      return `✓ Event deleted successfully\nEvent ID: ${args.eventId}`;
    } catch (error) {
      throw new Error(`Failed to delete event: ${error}`);
    }
  },
};

/**
 * Export all tools
 */
export const tools: Tool[] = [
  createEventTool,
  getEventTool,
  listEventsTool,
  getUpcomingEventsTool,
  updateEventTool,
  deleteEventTool,
];
