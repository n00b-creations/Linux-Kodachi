#!/usr/bin/env python3
"""CYBER-OS local API for Phase 1 with tool registry integration.

This service is intentionally localhost-only and read-oriented in the initial
release. It exposes platform health and discovered tool metadata without
modifying Kodachi services.

Features:
- Automatic tool discovery from registry
- Result caching with refresh capability
- Comprehensive error handling and logging
- Swagger/OpenAPI documentation
- Structured logging to file and stdout
"""

from __future__ import annotations

import json
import logging
import os
import platform
import shutil
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
except ImportError as exc:  # pragma: no cover - startup diagnostic
    raise SystemExit("FastAPI is required for the CYBER-OS API") from exc

# Configuration
APP_VERSION = "0.1.0-alpha"
CONFIG_ROOT = Path(os.environ.get("CYBER_OS_CONFIG_ROOT", "/etc/cyber-os"))
STATE_ROOT = Path(os.environ.get("CYBER_OS_STATE_ROOT", "/var/lib/cyber-os"))
LOG_ROOT = Path(os.environ.get("CYBER_OS_LOG_ROOT", "/var/log/cyber-os"))

# Ensure log directory exists
LOG_ROOT.mkdir(parents=True, exist_ok=True)

# Configure logging
log_file = LOG_ROOT / "cyber-os-api.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Try to import tool registry
try:
    from backend import tool_registry
    HAS_TOOL_REGISTRY = True
except ImportError:
    logger.warning("Tool registry module not available; using fallback tool discovery")
    HAS_TOOL_REGISTRY = False
    tool_registry = None

# FastAPI app
app = FastAPI(
    title="CYBER-OS API",
    version=APP_VERSION,
    description="Kodachi Cyber Operations Overlay - Phase 1 API",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Add CORS middleware (localhost-only by default)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1", "http://localhost"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Tool discovery cache
_tool_cache = None
_cache_timestamp = None
CACHE_TTL_SECONDS = 300  # 5 minutes


def _get_tool_status(executable: str) -> dict[str, Any]:
    """Get status of a single tool."""
    path = shutil.which(executable)
    return {"executable": executable, "installed": path is not None, "path": path}


def _discover_tools_fallback() -> list[dict[str, Any]]:
    """Fallback tool discovery (no registry)."""
    fallback_executables = ["git", "curl", "nmcli", "xfce4-terminal"]
    return [_get_tool_status(exe) for exe in fallback_executables]


def _discover_tools() -> list[dict[str, Any]]:
    """Discover tools from registry or fallback."""
    try:
        if HAS_TOOL_REGISTRY and tool_registry:
            logger.info("Using tool registry discovery")
            return tool_registry.discover()
        else:
            logger.info("Using fallback tool discovery")
            return _discover_tools_fallback()
    except Exception as e:
        logger.error(f"Tool discovery failed: {e}", exc_info=True)
        return _discover_tools_fallback()


def _get_cached_tools(refresh: bool = False) -> list[dict[str, Any]]:
    """Get tools with caching."""
    global _tool_cache, _cache_timestamp
    
    now = datetime.now().timestamp()
    
    if refresh or _tool_cache is None or (now - _cache_timestamp) > CACHE_TTL_SECONDS:
        logger.info("Refreshing tool cache")
        _tool_cache = _discover_tools()
        _cache_timestamp = now
    
    return _tool_cache


@app.on_event("startup")
async def startup_event():
    """Log startup event."""
    logger.info(f"CYBER-OS API starting (version {APP_VERSION})")
    logger.info(f"Config root: {CONFIG_ROOT}")
    logger.info(f"State root: {STATE_ROOT}")
    logger.info(f"Log root: {LOG_ROOT}")


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown event."""
    logger.info("CYBER-OS API shutting down")


@app.get("/health", tags=["System"])
async def health() -> dict[str, Any]:
    """Health check endpoint.
    
    Returns system health status, version, and configuration paths.
    """
    try:
        return {
            "status": "ok",
            "version": APP_VERSION,
            "platform": platform.platform(),
            "config_root": str(CONFIG_ROOT),
            "state_root": str(STATE_ROOT),
            "log_root": str(LOG_ROOT),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/system", tags=["System"])
async def system() -> dict[str, Any]:
    """System information endpoint.
    
    Returns hostname, kernel version, machine architecture, and Python version.
    """
    try:
        return {
            "hostname": platform.node(),
            "kernel": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "processor": platform.processor(),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"System info failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not retrieve system info")


@app.get("/tools", tags=["Tools"])
async def tools(refresh: bool = Query(False, description="Force refresh tool cache")) -> list[dict[str, Any]]:
    """Tool discovery endpoint.
    
    Returns list of discovered tools with installation status.
    
    Query Parameters:
    - refresh (bool): Force refresh the tool cache (default: false)
    """
    try:
        result = _get_cached_tools(refresh=refresh)
        logger.info(f"Returning {len(result)} tools (refresh={refresh})")
        return result
    except Exception as e:
        logger.error(f"Tool discovery failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Tool discovery failed")


@app.get("/info", tags=["System"])
async def info() -> dict[str, Any]:
    """Combined system and API information."""
    try:
        health_data = {
            "status": "ok",
            "version": APP_VERSION,
            "platform": platform.platform(),
        }
        system_data = {
            "hostname": platform.node(),
            "kernel": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        }
        return {
            "api": health_data,
            "system": system_data,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Info endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not retrieve info")


@app.get("/status", tags=["System"])
async def status() -> dict[str, Any]:
    """Extended status endpoint with cache and config status."""
    try:
        config_exists = CONFIG_ROOT.exists()
        state_exists = STATE_ROOT.exists()
        log_exists = LOG_ROOT.exists()
        
        return {
            "api": {
                "version": APP_VERSION,
                "status": "healthy",
                "tool_registry_enabled": HAS_TOOL_REGISTRY,
                "timestamp": datetime.utcnow().isoformat(),
            },
            "paths": {
                "config": {"path": str(CONFIG_ROOT), "exists": config_exists},
                "state": {"path": str(STATE_ROOT), "exists": state_exists},
                "logs": {"path": str(LOG_ROOT), "exists": log_exists},
            },
            "cache": {
                "tools_cached": _tool_cache is not None,
                "cache_ttl_seconds": CACHE_TTL_SECONDS,
            },
        }
    except Exception as e:
        logger.error(f"Status endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not retrieve status")


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler for unexpected errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


if __name__ == "__main__":
    # For development/testing
    import uvicorn
    logger.info("Starting CYBER-OS API in development mode")
    uvicorn.run(
        app,
        host=os.environ.get("CYBER_OS_BIND_HOST", "127.0.0.1"),
        port=int(os.environ.get("CYBER_OS_API_PORT", "8765")),
        log_config=None,  # Use our logging config
    )
