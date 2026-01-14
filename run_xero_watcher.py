#!/usr/bin/env python3
"""
Wrapper script for Xero Watcher (Direct SDK version - NOT MCP version)

This wrapper ensures the watchers module can be found by setting the Python path correctly.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Now run the actual watcher with the same arguments
# CHANGE: Use xero_watcher.py instead of xero_watcher_mcp.py
from watchers.xero_watcher import main

if __name__ == "__main__":
    main()
