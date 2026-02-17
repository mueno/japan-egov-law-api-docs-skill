#!/usr/bin/env python3
"""Compatibility wrapper for the packaged e-Gov CLI."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from egov_law_api.cli import run


if __name__ == "__main__":
    run()
