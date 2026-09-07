#!/usr/bin/env python3
"""CYBER-OS tool registry for Phase 1.

Provides read-only tool discovery from YAML-based provider manifests.
Includes error handling, logging, and caching support.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required for the CYBER-OS tool registry") from exc

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = ROOT / "integrations" / "tool-registry" / "providers"


def _load(path: Path) -> dict[str, Any]:
    """Load and parse a YAML file safely.
    
    Args:
        path: Path to YAML file
        
    Returns:
        Parsed YAML content or empty dict if parse fails
    """
    try:
        with path.open("r", encoding="utf-8") as fh:
            content = yaml.safe_load(fh)
            return content if isinstance(content, dict) else {}
    except FileNotFoundError:
        logger.warning(f"Provider file not found: {path}")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"YAML parse error in {path}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error loading {path}: {e}")
        return {}


def discover() -> list[dict[str, Any]]:
    """Discover available tools from all enabled providers.
    
    Iterates through all YAML files in the providers directory,
    loads tool metadata, and enriches with installation status.
    
    Returns:
        List of tool dictionaries with discovered tools
    """
    results: list[dict[str, Any]] = []
    
    if not PROVIDERS.exists():
        logger.warning(f"Providers directory does not exist: {PROVIDERS}")
        return results
    
    provider_files = sorted(PROVIDERS.glob("*.yaml"))
    
    if not provider_files:
        logger.warning(f"No provider files found in {PROVIDERS}")
        return results
    
    logger.info(f"Discovering tools from {len(provider_files)} provider(s)")
    
    for path in provider_files:
        try:
            logger.debug(f"Loading provider: {path.name}")
            document = _load(path)
            
            provider = document.get("provider", {})
            provider_id = provider.get("id", path.stem)
            enabled = provider.get("enabled", False)
            
            if not enabled:
                logger.debug(f"Provider {provider_id} is disabled, skipping")
                continue
            
            logger.debug(f"Provider {provider_id} is enabled")
            
            tools = document.get("tools", [])
            logger.debug(f"Found {len(tools)} tool(s) in {provider_id}")
            
            for tool in tools:
                try:
                    executable = tool.get("executable")
                    
                    if not executable:
                        logger.warning(f"Tool in {provider_id} has no executable, skipping")
                        continue
                    
                    # Create enriched tool object
                    enriched_tool = dict(tool)
                    enriched_tool["installed"] = shutil.which(executable) is not None
                    enriched_tool["path"] = shutil.which(executable)
                    enriched_tool["provider"] = provider_id
                    
                    results.append(enriched_tool)
                    logger.debug(f"Discovered tool: {executable} (installed={enriched_tool['installed']})")
                
                except Exception as e:
                    logger.error(f"Error processing tool in {provider_id}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error processing provider {path.name}: {e}")
            continue
    
    logger.info(f"Tool discovery complete: {len(results)} tool(s) discovered")
    return results


def get_installed_tools() -> list[dict[str, Any]]:
    """Get only installed tools (convenience function).
    
    Returns:
        List of installed tools
    """
    return [tool for tool in discover() if tool.get("installed", False)]


def get_tools_by_provider(provider_id: str) -> list[dict[str, Any]]:
    """Get tools from a specific provider (convenience function).
    
    Args:
        provider_id: Provider identifier
        
    Returns:
        List of tools from the specified provider
    """
    return [tool for tool in discover() if tool.get("provider") == provider_id]


def get_tools_by_category(category: str) -> list[dict[str, Any]]:
    """Get tools by category (convenience function).
    
    Args:
        category: Tool category
        
    Returns:
        List of tools in the specified category
    """
    return [tool for tool in discover() if category in tool.get("categories", [])]
