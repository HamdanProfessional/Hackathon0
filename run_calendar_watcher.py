#!/usr/bin/env python3
"""
Wrapper script for Calendar Watcher - Runs as a module to fix relative imports.
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Run the watcher as a module
if __name__ == "__main__":
    from watchers.calendar_watcher import main
    main()
