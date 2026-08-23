#!/usr/bin/env python3
"""Minimal CYBER-OS local API for Phase 1.

This service is intentionally localhost-only and read-oriented in the initial
release. It exposes platform health and discovered tool metadata without
modifying Kodachi services.
"""

from __future__ import annotations

import os
import platform
import shutil
from pathlib import Path
from typing import Any

try:
    from fastapi import FastAPI
except ImportError as exc:  # pragma: no cover - startup diagnostic
    raise SystemExit("FastAPI is required for the CYBER-OS API") from exc

APP_VERSION = "0.1.0-alpha"
CONFIG_ROOT = Path(os.environ.get("CYBER_OS_CONFIG_ROOT", "/etc/cyber-os"))
STATE_ROOT = Path(os.environ.get("CYBER_OS_STATE_ROOT", "/var/lib/cyber-os"))

app = FastAPI(title="CYBER-OS API", version=APP_VERSION)


def _tool_status(executable: str) -> dict[str, Any]:
    path = shutil.which(executable)
    return {"executable": executable, "installed": path is not None, "path": path}


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "version": APP_VERSION,
        "platform": platform.platform(),
        "config_root": str(CONFIG_ROOT),
        "state_root": str(STATE_ROOT),
    }


@app.get("/system")
def system() -> dict[str, Any]:
    return {
        "hostname": platform.node(),
        "kernel": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
    }


@app.get("/tools")
def tools() -> list[dict[str, Any]]:
    executables = ["git", "curl", "nmcli", "xfce4-terminal"]
    return [_tool_status(item) for item in executables]
