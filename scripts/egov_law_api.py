#!/usr/bin/env python3
"""Compatibility wrapper for the packaged e-Gov CLI."""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"


def main() -> None:
    env = dict(os.environ)
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        f"{SRC_DIR}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else str(SRC_DIR)
    )
    cmd = [sys.executable, "-m", "egov_law_api.cli", *sys.argv[1:]]
    os.execvpe(cmd[0], cmd, env)


if __name__ == "__main__":
    main()
