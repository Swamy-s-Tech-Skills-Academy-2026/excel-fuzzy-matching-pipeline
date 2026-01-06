#!/usr/bin/env python3
"""
Run the Excel Fuzzy Matching Pipeline from project root.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print(f"Project root set to: {project_root}")

# Import and run main
try:
    from src.main import main, setup_logging
except ModuleNotFoundError as e:
    missing = getattr(e, "name", None)
    if missing in {"pandas", "openpyxl", "rapidfuzz"}:
        sys.stderr.write(
            "\n[ERROR] Missing dependency: {0}\n".format(missing)
            + "This commonly happens on Windows when running via `py`, which may bypass your virtual environment.\n\n"
            + "Run one of these instead (from project root):\n"
            + "  - .\\.venv\\Scripts\\python.exe .\\run_pipeline.py\n"
            + "  - Activate venv, then: python .\\run_pipeline.py\n\n"
            + "Or install dependencies into the interpreter you're using:\n"
            + "  python -m pip install -r requirements.txt\n\n"
        )
        raise SystemExit(1)
    raise

if __name__ == "__main__":
    setup_logging()
    sys.exit(main())
