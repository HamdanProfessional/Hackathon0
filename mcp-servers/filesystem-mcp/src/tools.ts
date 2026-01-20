/**
 * MCP Tool Definitions for Filesystem
 */

import { FilesystemClient } from "./filesystem-client.js";

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
  handler: (client: FilesystemClient, args: any) => Promise<string>;
}

export const tools: Tool[] = [
  {
    name: "list_directory",
    description: "List all files and subdirectories in a directory",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "Directory path to list (relative or absolute)",
        },
      },
      required: ["path"],
    },
    handler: async (client, args) => {
      const files = await client.listDirectory(args.path);

      if (files.length === 0) {
        return `Directory is empty: ${args.path}`;
      }

      const fileList = files
        .map((f) => {
          const icon = f.type === "directory" ? "📁" : "📄";
          const size = f.size !== undefined ? ` (${f.size} bytes)` : "";
          return `${icon} ${f.name}${size}`;
        })
        .join("\n");

      return `Contents of ${args.path}:\n\n${fileList}`;
    },
  },

  {
    name: "read_file",
    description: "Read the contents of a text file",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "File path to read (relative or absolute)",
        },
      },
      required: ["path"],
    },
    handler: async (client, args) => {
      const content = await client.readFile(args.path);

      // Truncate if too long
      const maxLength = 10000;
      if (content.length > maxLength) {
        return `${content.substring(0, maxLength)}\n\n[... Truncated: File too long (${content.length} chars) ...]`;
      }

      return content;
    },
  },

  {
    name: "write_file",
    description: "Write content to a file (creates file if it doesn't exist)",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "File path to write (relative or absolute)",
        },
        content: {
          type: "string",
          description: "Content to write to the file",
        },
      },
      required: ["path", "content"],
    },
    handler: async (client, args) => {
      return await client.writeFile(args.path, args.content);
    },
  },

  {
    name: "delete_file",
    description: "Delete a file (use with caution)",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "File path to delete (relative or absolute)",
        },
      },
      required: ["path"],
    },
    handler: async (client, args) => {
      return await client.deleteFile(args.path);
    },
  },

  {
    name: "get_file_info",
    description: "Get detailed metadata about a file or directory",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "File or directory path (relative or absolute)",
        },
      },
      required: ["path"],
    },
    handler: async (client, args) => {
      return await client.getFileInfo(args.path);
    },
  },

  {
    name: "create_directory",
    description: "Create a new directory (including parent directories if needed)",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "Directory path to create (relative or absolute)",
        },
      },
      required: ["path"],
    },
    handler: async (client, args) => {
      return await client.createDirectory(args.path);
    },
  },

  {
    name: "watch_directory",
    description: "Watch a directory for file changes (creates, modifies, deletes)",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "Directory path to watch (relative or absolute)",
        },
      },
      required: ["path"],
    },
    handler: async (client, args) => {
      // Start watching and set up callback to log changes
      const watchedDirs = client.getWatchedDirectories();

      // Check if already watching
      if (watchedDirs.includes(args.path)) {
        return `Already watching: ${args.path}`;
      }

      await client.watchDirectory(
        args.path,
        (filePath, type) => {
          console.log(`[Filesystem Watch] ${type}: ${filePath}`);
        },
        {
          ignoreInitial: true,
        }
      );

      return `Now watching directory: ${args.path}\nChanges will be logged to console.`;
    },
  },

  {
    name: "stop_watching",
    description: "Stop watching a directory",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "Directory path to stop watching",
        },
      },
      required: ["path"],
    },
    handler: async (client, args) => {
      const watchedDirs = client.getWatchedDirectories();

      if (!watchedDirs.includes(args.path)) {
        return `Not watching: ${args.path}\n\nCurrently watching:\n${watchedDirs.join("\n") || "(none)"}`;
      }

      client.stopWatching(args.path);
      return `Stopped watching: ${args.path}`;
    },
  },

  {
    name: "list_watched",
    description: "List all directories currently being watched",
    inputSchema: {
      type: "object",
      properties: {},
    },
    handler: async (client) => {
      const watchedDirs = client.getWatchedDirectories();

      if (watchedDirs.length === 0) {
        return "No directories are currently being watched.";
      }

      return `Currently watching ${watchedDirs.length} director${watchedDirs.length === 1 ? "y" : "ies"}:\n\n${watchedDirs.join("\n")}`;
    },
  },

  {
    name: "search_files",
    description: "Search for files by name pattern (supports regex)",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "Directory path to search in (relative or absolute)",
        },
        pattern: {
          type: "string",
          description: "Regex pattern to match file names (e.g., '\\.md$' for markdown files)",
        },
        max_results: {
          type: "string",
          description: "Maximum number of results to return (default: 100)",
        },
      },
      required: ["path", "pattern"],
    },
    handler: async (client, args) => {
      const maxResults = args.max_results ? parseInt(args.max_results) : 100;
      return await client.searchFiles(args.path, args.pattern, maxResults);
    },
  },

  {
    name: "append_file",
    description: "Append content to an existing file",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "File path to append to (relative or absolute)",
        },
        content: {
          type: "string",
          description: "Content to append to the file",
        },
      },
      required: ["path", "content"],
    },
    handler: async (client, args) => {
      const { path, content } = args;

      try {
        // Read existing content
        const existingContent = await client.readFile(path);
        // Append new content
        return await client.writeFile(path, existingContent + content);
      } catch {
        // If file doesn't exist, just create it with the content
        return await client.writeFile(path, content);
      }
    },
  },
];
