#!/usr/bin/env python3
"""
Run the Excel Fuzzy Matching Pipeline from project root.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run main
from src.main import main, setup_logging

if __name__ == "__main__":
    setup_logging()
    sys.exit(main())
