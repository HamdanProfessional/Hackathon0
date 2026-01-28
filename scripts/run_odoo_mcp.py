#!/usr/bin/env python3
"""
Odoo MCP Server - Standalone CLI Runner

Run the Odoo MCP server directly without pip installation issues.

Usage:
    python scripts/run_odoo_mcp.py --transport stdio
    python scripts/run_odoo_mcp.py --transport sse --host 0.0.0.0 --port 8080
"""
import argparse
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add MCP server to path
odoo_mcp_path = project_root / "mcp-servers" / "odoo-mcp"
sys.path.insert(0, str(odoo_mcp_path))

# Import the server components
from mcp_instance import mcp
from config import config
from fastmcp import ClientSession, ServerSettings
import uvicorn


def main():
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="Odoo MCP Server")
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport to use: stdio (local agents) or sse (HTTP server)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host for SSE transport"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for SSE transport"
    )

    args = parser.parse_args()

    # Validate config
    if not config.validate():
        print("ERROR: Invalid Odoo configuration", file=sys.stderr)
        print("Please check mcp-servers/odoo-mcp/.env", file=sys.stderr)
        sys.exit(1)

    print(f"[Odoo MCP] Starting with {args.transport} transport...", file=sys.stderr)
    print(f"[Odoo MCP] Connected to: {config.odoo.url}", file=sys.stderr)
    print(f"[Odoo MCP] Database: {config.odoo.database}", file=sys.stderr)

    if args.transport == "sse":
        # Run as HTTP server with SSE support
        print(f"[Odoo MCP] Starting SSE server on http://{args.host}:{args.port}", file=sys.stderr)

        # Import mcp_instance SSE support
        import asyncio
        from starlette.applications import Starlette
        from starlette.routing import Route
        from starlette.responses import Response
        import json

        # Create a simple SSE server
        app = Starlette(debug=True)

        @app.route("/sse")
        async def sse_endpoint(request):
            """SSE endpoint for MCP."""
            from fastmcp.server import FastMCP
            from fastmcp.transports.sse import SseServerTransport

            # Create SSE transport
            transport = SseServerTransport("/messages")

            # Run the MCP server
            async def run_mcp():
                await mcp.run(transport)

            asyncio.create_task(run_mcp())

            return Response(content="SSE endpoint active", media_type="text/plain")

        @app.route("/messages")
        async def messages_endpoint(request):
            """Messages endpoint for MCP."""
            return Response(content="Messages endpoint", media_type="text/plain")

        @app.route("/")
        async def root(request):
            """Root endpoint with server info."""
            info = {
                "server": "Odoo MCP",
                "version": "0.1.0",
                "endpoints": {
                    "sse": f"http://{args.host}:{args.port}/sse",
                    "messages": f"http://{args.host}:{args.port}/messages"
                },
                "odoo": {
                    "url": config.odoo.url,
                    "database": config.odoo.database
                }
            }
            return Response(content=json.dumps(info, indent=2), media_type="application/json")

        # Run with uvicorn
        uvicorn.run(app, host=args.host, port=args.port)

    else:
        # Run with stdio transport
        print("[Odoo MCP] Starting stdio transport...", file=sys.stderr)

        # Import and run stdio transport
        from fastmcp.transports.stdio import StdioServerTransport

        transport = StdioServerTransport()

        # Run the MCP server
        async def run_stdio():
            await mcp.run(transport)

        asyncio.run(run_stdio())


if __name__ == "__main__":
    main()
