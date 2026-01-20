# Filesystem MCP Server

Model Context Protocol server for filesystem operations. Provides tools for watching directories, reading/writing files, and file management.

## Features

### Available Tools

| Tool | Description |
|------|-------------|
| `list_directory` | List all files and subdirectories in a directory |
| `read_file` | Read the contents of a text file |
| `write_file` | Write content to a file (creates if doesn't exist) |
| `append_file` | Append content to an existing file |
| `delete_file` | Delete a file |
| `get_file_info` | Get detailed metadata about a file or directory |
| `create_directory` | Create a new directory (including parents) |
| `watch_directory` | Watch a directory for file changes |
| `stop_watching` | Stop watching a directory |
| `list_watched` | List all directories currently being watched |
| `search_files` | Search for files by name pattern (regex) |

## Installation

```bash
cd mcp-servers/filesystem-mcp
npm install
npm run build
```

## Configuration

Set the base directory for filesystem operations:

```bash
export FILESYSTEM_BASE_DIR=/path/to/your/vault
```

Default: Current working directory

## Usage

### Start the MCP server

```bash
npm start
# or
node dist/index.js
```

### Example Tool Calls

**List directory contents:**
```json
{
  "name": "list_directory",
  "arguments": {
    "path": "AI_Employee_Vault/Inbox"
  }
}
```

**Read a file:**
```json
{
  "name": "read_file",
  "arguments": {
    "path": "AI_Employee_Vault/Dashboard.md"
  }
}
```

**Write a file:**
```json
{
  "name": "write_file",
  "arguments": {
    "path": "AI_Employee_Vault/Needs_Action/test.md",
    "content": "# Test\n\nThis is a test file."
  }
}
```

**Watch a directory:**
```json
{
  "name": "watch_directory",
  "arguments": {
    "path": "AI_Employee_Vault/Inbox"
  }
}
```

**Search for files:**
```json
{
  "name": "search_files",
  "arguments": {
    "path": "AI_Employee_Vault",
    "pattern": "\\.md$",
    "max_results": "50"
  }
}
```

## Integration with Claude Code

Add to your Claude Code MCP configuration (`~/.config/claude-code/mcp.json`):

```json
{
  "servers": [
    {
      "name": "filesystem",
      "command": "node",
      "args": ["C:\\Users\\User\\Desktop\\AI_EMPLOYEE_APP\\mcp-servers\\filesystem-mcp\\dist\\index.js"],
      "env": {
        "FILESYSTEM_BASE_DIR": "C:\\Users\\User\\Desktop\\AI_EMPLOYEE_APP\\AI_Employee_Vault"
      }
    }
  ]
}
```

## Development

```bash
# Build TypeScript
npm run build

# Watch mode for development
npm run watch

# Run tests
node test.cjs
```

## Architecture

```
src/
├── index.ts              # MCP server setup and tool routing
├── filesystem-client.ts  # Core filesystem operations
├── tools.ts              # MCP tool definitions
└── dist/                 # Compiled JavaScript output
```

## Dependencies

- `@modelcontextprotocol/sdk` - MCP SDK
- `chokidar` - File watching with native efficiency
- `typescript` - Type safety

## Security Notes

⚠️ **Important:** This MCP server provides direct filesystem access. Ensure:

1. Only watch directories you trust
2. Set appropriate `FILESYSTEM_BASE_DIR` to limit access
3. Review Claude's proposed file operations before approving
4. Never expose this server to network access

## License

MIT
