#!/usr/bin/env python3
"""CYBER-OS Overlay API (FastAPI)

Endpoints:
- /health
- /system
- /tools
- /admin/reload-registry (localhost-only)

Uses integrations.tool_registry to discover tools from YAML providers.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
import shutil
from typing import List

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import psutil

from .tool_registry import ToolRegistry

# Configuration from env
PREFIX = os.environ.get("CYBER_OS_PREFIX", "/opt/cyber-os")
LOG_DIR = os.environ.get("CYBER_OS_LOG_DIR", "/var/log/cyber-os")
BIND_HOST = os.environ.get("CYBER_OS_BIND_HOST", "127.0.0.1")
API_PORT = int(os.environ.get("CYBER_OS_API_PORT", "8765"))

os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "cyber-os-api.log")

logger = logging.getLogger("cyber_os_api")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(LOG_PATH, maxBytes=5_000_000, backupCount=3)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

app = FastAPI(title="CYBER-OS Overlay API")

# Tool registry instance (with simple caching)
_registry = ToolRegistry()
_tool_cache = None


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"error": "internal_server_error"})


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/system")
async def system_info():
    try:
        info = {
            "cpu_count": psutil.cpu_count(logical=True),
            "memory_total": psutil.virtual_memory().total,
            "disk_root": psutil.disk_usage("/").total,
            "prefix": PREFIX,
        }
        return info
    except Exception as e:
        logger.exception("Failed to read system info")
        raise HTTPException(status_code=500, detail="failed_to_read_system_info")


@app.get("/tools")
async def tools(refresh: bool = False):
    global _tool_cache
    try:
        if _tool_cache is None or refresh:
            logger.info("Discovering tools (refresh=%s)", refresh)
            _tool_cache = _registry.discover()
        return {"tools": _tool_cache}
    except FileNotFoundError as e:
        logger.exception("Tool registry not found")
        raise HTTPException(status_code=500, detail="tool_registry_not_found")
    except Exception as e:
        logger.exception("Tool discovery failed: %s", e)
        raise HTTPException(status_code=500, detail="tool_discovery_failed")


def _is_localhost(request: Request) -> bool:
    host = request.client.host if request.client else None
    return host in ("127.0.0.1", "::1", "localhost")


@app.post("/admin/reload-registry")
async def reload_registry(request: Request):
    if not _is_localhost(request):
        raise HTTPException(status_code=403, detail="forbidden")
    try:
        logger.info("Reloading tool registry per admin request")
        _registry.reload()
        # force refresh
        global _tool_cache
        _tool_cache = _registry.discover()
        return {"reloaded": True}
    except Exception as e:
        logger.exception("Failed to reload registry")
        raise HTTPException(status_code=500, detail="reload_failed")
