#!/usr/bin/env python3
"""
Wrapper script for Xero Watcher (MCP version)

This wrapper ensures the watchers module can be found by setting the Python path correctly.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now run the actual watcher with the same arguments
from watchers.xero_watcher_mcp import main

if __name__ == "__main__":
    main()
