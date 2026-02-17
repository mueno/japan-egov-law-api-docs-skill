#!/usr/bin/env python3
"""Compatibility wrapper for the packaged e-Gov MCP server."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from egov_law_api.mcp_server import main


if __name__ == "__main__":
    main()
