#!/usr/bin/env python3
"""
Wrapper script for Xero Watcher (Direct SDK version - NOT MCP version).
Located in scripts/ folder, adds parent directory to Python path.
"""
import sys
from pathlib import Path

# Add parent directory (project root) to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Run the actual watcher
from watchers.xero_watcher import main

if __name__ == "__main__":
    main()
