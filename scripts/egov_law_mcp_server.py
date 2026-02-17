#!/usr/bin/env python3
"""Compatibility wrapper for the packaged e-Gov MCP server."""

from __future__ import annotations

import os
import sys
from importlib.util import find_spec
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"


def main() -> None:
    if find_spec("mcp") is None:
        print(
            "Missing dependency: mcp. Run `uv sync` (recommended) or "
            "`python3 -m pip install -r requirements.txt` first.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    env = dict(os.environ)
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        f"{SRC_DIR}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else str(SRC_DIR)
    )
    cmd = [sys.executable, "-m", "egov_law_api.mcp_server", *sys.argv[1:]]
    os.execvpe(cmd[0], cmd, env)


if __name__ == "__main__":
    main()
