#!/usr/bin/env python3
"""
Wrapper script for Slack Watcher - Runs as a module to fix relative imports.
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Run the watcher as a module
if __name__ == "__main__":
    from watchers.slack_watcher import main
    main()
