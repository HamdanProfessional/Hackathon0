/**
 * Filesystem Client
 *
 * Handles file and directory operations including watching for changes.
 */

import * as fs from "fs/promises";
import * as path from "path";
import { existsSync, Stats as FsStats } from "fs";
import { watch } from "chokidar";

export interface WatchOptions {
  persistent?: boolean;
  ignoreInitial?: boolean;
  awaitWriteFinish?: boolean | {
    stabilityThreshold?: number;
    pollInterval?: number;
  };
}

export interface FileInfo {
  name: string;
  path: string;
  type: "file" | "directory";
  size?: number;
  modified?: Date;
  created?: Date;
}

export class FilesystemClient {
  private watchers: Map<string, any> = new Map();
  private changeCallbacks: Map<string, (filePath: string, type: string) => void> = new Map();

  /**
   * List contents of a directory
   */
  async listDirectory(dirPath: string): Promise<FileInfo[]> {
    try {
      const absolutePath = path.resolve(dirPath);

      if (!existsSync(absolutePath)) {
        throw new Error(`Directory does not exist: ${dirPath}`);
      }

      const entries = await fs.readdir(absolutePath, { withFileTypes: true });
      const files: FileInfo[] = [];

      for (const entry of entries) {
        const fullPath = path.join(absolutePath, entry.name);
        let stats: FsStats | undefined;

        try {
          stats = await fs.stat(fullPath);
        } catch {
          // Skip if can't get stats
        }

        files.push({
          name: entry.name,
          path: fullPath,
          type: entry.isDirectory() ? "directory" : "file",
          size: stats?.size,
          modified: stats?.mtime,
          created: stats?.birthtime,
        });
      }

      return files;
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to list directory: ${error.message}`);
      }
      throw error;
    }
  }

  /**
   * Read file contents
   */
  async readFile(filePath: string): Promise<string> {
    try {
      const absolutePath = path.resolve(filePath);

      if (!existsSync(absolutePath)) {
        throw new Error(`File does not exist: ${filePath}`);
      }

      const content = await fs.readFile(absolutePath, "utf-8");
      return content;
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to read file: ${error.message}`);
      }
      throw error;
    }
  }

  /**
   * Write file contents
   */
  async writeFile(filePath: string, content: string): Promise<string> {
    try {
      const absolutePath = path.resolve(filePath);

      // Ensure directory exists
      const dir = path.dirname(absolutePath);
      if (!existsSync(dir)) {
        await fs.mkdir(dir, { recursive: true });
      }

      await fs.writeFile(absolutePath, content, "utf-8");
      return `File written successfully: ${absolutePath}`;
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to write file: ${error.message}`);
      }
      throw error;
    }
  }

  /**
   * Delete a file
   */
  async deleteFile(filePath: string): Promise<string> {
    try {
      const absolutePath = path.resolve(filePath);

      if (!existsSync(absolutePath)) {
        throw new Error(`File does not exist: ${filePath}`);
      }

      await fs.unlink(absolutePath);
      return `File deleted successfully: ${absolutePath}`;
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to delete file: ${error.message}`);
      }
      throw error;
    }
  }

  /**
   * Get file information
   */
  async getFileInfo(filePath: string): Promise<string> {
    try {
      const absolutePath = path.resolve(filePath);

      if (!existsSync(absolutePath)) {
        throw new Error(`File does not exist: ${filePath}`);
      }

      const stats = await fs.stat(absolutePath);
      const isDirectory = stats.isDirectory();

      return `Path: ${absolutePath}
Type: ${isDirectory ? "Directory" : "File"}
Size: ${stats.size} bytes
Modified: ${stats.mtime.toISOString()}
Created: ${stats.birthtime.toISOString()}
Permissions: ${stats.mode.toString(8)}`;
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to get file info: ${error.message}`);
      }
      throw error;
    }
  }

  /**
   * Create a directory
   */
  async createDirectory(dirPath: string): Promise<string> {
    try {
      const absolutePath = path.resolve(dirPath);

      if (existsSync(absolutePath)) {
        throw new Error(`Directory already exists: ${dirPath}`);
      }

      await fs.mkdir(absolutePath, { recursive: true });
      return `Directory created successfully: ${absolutePath}`;
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to create directory: ${error.message}`);
      }
      throw error;
    }
  }

  /**
   * Watch a directory for changes
   */
  async watchDirectory(
    dirPath: string,
    callback: (filePath: string, type: string) => void,
    options: WatchOptions = {}
  ): Promise<string> {
    try {
      const absolutePath = path.resolve(dirPath);

      if (!existsSync(absolutePath)) {
        throw new Error(`Directory does not exist: ${dirPath}`);
      }

      // Stop existing watcher for this path if any
      this.stopWatching(dirPath);

      // Create new watcher
      const watcher = watch(absolutePath, {
        persistent: options.persistent ?? true,
        ignoreInitial: options.ignoreInitial ?? true,
        awaitWriteFinish: options.awaitWriteFinish ?? {
          stabilityThreshold: 200,
          pollInterval: 100,
        },
      });

      // Set up event handlers
      watcher.on("all", (event: string, watchedPath: string) => {
        callback(watchedPath, event);
      });

      watcher.on("error", (error: unknown) => {
        console.error(`Watcher error for ${dirPath}:`, error);
      });

      // Store watcher and callback
      this.watchers.set(dirPath, watcher);
      this.changeCallbacks.set(dirPath, callback);

      return `Now watching: ${absolutePath}`;
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to watch directory: ${error.message}`);
      }
      throw error;
    }
  }

  /**
   * Stop watching a directory
   */
  stopWatching(dirPath: string): void {
    const watcher = this.watchers.get(dirPath);
    if (watcher) {
      watcher.close();
      this.watchers.delete(dirPath);
      this.changeCallbacks.delete(dirPath);
    }
  }

  /**
   * Stop all watchers
   */
  stopAllWatchers(): void {
    for (const [dirPath] of this.watchers) {
      this.stopWatching(dirPath);
    }
  }

  /**
   * Get list of currently watched directories
   */
  getWatchedDirectories(): string[] {
    return Array.from(this.watchers.keys());
  }

  /**
   * Search for files by pattern
   */
  async searchFiles(
    dirPath: string,
    pattern: string,
    maxResults: number = 100
  ): Promise<string> {
    try {
      const absolutePath = path.resolve(dirPath);

      if (!existsSync(absolutePath)) {
        throw new Error(`Directory does not exist: ${dirPath}`);
      }

      const regex = new RegExp(pattern, "i");
      const matches: string[] = [];

      const searchDir = async (currentPath: string): Promise<void> => {
        if (matches.length >= maxResults) return;

        try {
          const entries = await fs.readdir(currentPath, { withFileTypes: true });

          for (const entry of entries) {
            if (matches.length >= maxResults) break;

            const fullPath = path.join(currentPath, entry.name);

            if (entry.name.match(regex)) {
              matches.push(fullPath);
            }

            if (entry.isDirectory()) {
              await searchDir(fullPath);
            }
          }
        } catch {
          // Skip directories we can't read
        }
      };

      await searchDir(absolutePath);

      if (matches.length === 0) {
        return `No matches found for pattern: ${pattern}`;
      }

      return `Found ${matches.length} matches:\n${matches.join("\n")}`;
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Search failed: ${error.message}`);
      }
      throw error;
    }
  }
}
