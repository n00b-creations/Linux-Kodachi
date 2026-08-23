#!/usr/bin/env python3
"""Read-only CYBER-OS tool registry for Phase 1D."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required for the CYBER-OS tool registry") from exc

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = ROOT / "integrations" / "tool-registry" / "providers"


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def discover() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for path in sorted(PROVIDERS.glob("*.yaml")):
        document = _load(path)
        provider = document.get("provider", {})
        if not provider.get("enabled", False):
            continue
        for tool in document.get("tools", []):
            executable = tool.get("executable")
            if not executable:
                continue
            tool = dict(tool)
            tool["installed"] = shutil.which(executable) is not None
            tool["path"] = shutil.which(executable)
            results.append(tool)
    return results
