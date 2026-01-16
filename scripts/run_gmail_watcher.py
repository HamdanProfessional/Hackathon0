#!/usr/bin/env python3
"""
Wrapper script for Gmail Watcher - Runs as a module to fix relative imports.
Located in scripts/ folder, adds parent directory to Python path.
"""
import sys
import os
from pathlib import Path

# Add parent directory (project root) to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Run the watcher as a module
if __name__ == "__main__":
    from watchers.gmail_watcher import main
    main()
