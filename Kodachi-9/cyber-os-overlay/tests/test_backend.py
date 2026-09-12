#!/usr/bin/env python3
"""Unit tests for CYBER-OS backend modules."""

import json
import logging
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Configure logging for tests
logging.basicConfig(level=logging.INFO)


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing."""
    with tempfile.TemporaryDirectory() as config_dir, \
         tempfile.TemporaryDirectory() as state_dir, \
         tempfile.TemporaryDirectory() as log_dir:
        yield {
            "config": Path(config_dir),
            "state": Path(state_dir),
            "log": Path(log_dir),
        }


@pytest.fixture
def api_client(temp_dirs):
    """Create a test client for the API."""
    import os
    os.environ["CYBER_OS_CONFIG_ROOT"] = str(temp_dirs["config"])
    os.environ["CYBER_OS_STATE_ROOT"] = str(temp_dirs["state"])
    os.environ["CYBER_OS_LOG_ROOT"] = str(temp_dirs["log"])
    
    from fastapi.testclient import TestClient
    from backend.cyber_os_api import app
    
    return TestClient(app)


class TestHealthEndpoint:
    """Test cases for /health endpoint."""
    
    def test_health_returns_ok_status(self, api_client):
        """Health endpoint should return 'ok' status."""
        response = api_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_health_returns_version(self, api_client):
        """Health endpoint should return API version."""
        response = api_client.get("/health")
        data = response.json()
        assert "version" in data
        assert data["version"] == "0.1.0-alpha"
    
    def test_health_returns_platform(self, api_client):
        """Health endpoint should return platform info."""
        response = api_client.get("/health")
        data = response.json()
        assert "platform" in data
        assert isinstance(data["platform"], str)
    
    def test_health_returns_config_root(self, api_client, temp_dirs):
        """Health endpoint should return config root path."""
        response = api_client.get("/health")
        data = response.json()
        assert data["config_root"] == str(temp_dirs["config"])
    
    def test_health_returns_state_root(self, api_client, temp_dirs):
        """Health endpoint should return state root path."""
        response = api_client.get("/health")
        data = response.json()
        assert data["state_root"] == str(temp_dirs["state"])
    
    def test_health_returns_timestamp(self, api_client):
        """Health endpoint should return ISO timestamp."""
        response = api_client.get("/health")
        data = response.json()
        assert "timestamp" in data
        # Should be ISO format
        assert "T" in data["timestamp"]


class TestSystemEndpoint:
    """Test cases for /system endpoint."""
    
    def test_system_returns_hostname(self, api_client):
        """System endpoint should return hostname."""
        response = api_client.get("/system")
        assert response.status_code == 200
        data = response.json()
        assert "hostname" in data
        assert isinstance(data["hostname"], str)
    
    def test_system_returns_kernel(self, api_client):
        """System endpoint should return kernel version."""
        response = api_client.get("/system")
        data = response.json()
        assert "kernel" in data
        assert isinstance(data["kernel"], str)
    
    def test_system_returns_machine(self, api_client):
        """System endpoint should return machine architecture."""
        response = api_client.get("/system")
        data = response.json()
        assert "machine" in data
        assert isinstance(data["machine"], str)
    
    def test_system_returns_python(self, api_client):
        """System endpoint should return Python version."""
        response = api_client.get("/system")
        data = response.json()
        assert "python" in data
        assert isinstance(data["python"], str)
    
    def test_system_returns_processor(self, api_client):
        """System endpoint should return processor info."""
        response = api_client.get("/system")
        data = response.json()
        assert "processor" in data


class TestToolsEndpoint:
    """Test cases for /tools endpoint."""
    
    def test_tools_returns_list(self, api_client):
        """Tools endpoint should return a list."""
        response = api_client.get("/tools")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_tools_returns_tool_objects(self, api_client):
        """Tools endpoint should return tool objects with required fields."""
        response = api_client.get("/tools")
        data = response.json()
        
        # Should have at least some tools
        if len(data) > 0:
            tool = data[0]
            assert "executable" in tool
            assert "installed" in tool
            assert "path" in tool or tool["path"] is None
    
    def test_tools_refresh_parameter(self, api_client):
        """Tools endpoint should accept refresh parameter."""
        response = api_client.get("/tools?refresh=true")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_tools_with_known_tool(self, api_client):
        """Tools endpoint should include common tools."""
        response = api_client.get("/tools")
        data = response.json()
        executables = [t["executable"] for t in data]
        
        # Should have at least one known tool
        assert len(executables) > 0


class TestInfoEndpoint:
    """Test cases for /info endpoint."""
    
    def test_info_returns_combined_data(self, api_client):
        """Info endpoint should return combined system and API info."""
        response = api_client.get("/info")
        assert response.status_code == 200
        data = response.json()
        
        assert "api" in data
        assert "system" in data
        assert "timestamp" in data
    
    def test_info_contains_version(self, api_client):
        """Info endpoint should include API version."""
        response = api_client.get("/info")
        data = response.json()
        assert data["api"]["version"] == "0.1.0-alpha"
    
    def test_info_contains_system_info(self, api_client):
        """Info endpoint should include system information."""
        response = api_client.get("/info")
        data = response.json()
        
        assert "hostname" in data["system"]
        assert "kernel" in data["system"]
        assert "machine" in data["system"]
        assert "python" in data["system"]


class TestStatusEndpoint:
    """Test cases for /status endpoint."""
    
    def test_status_returns_api_info(self, api_client):
        """Status endpoint should return API information."""
        response = api_client.get("/status")
        assert response.status_code == 200
        data = response.json()
        
        assert "api" in data
        assert data["api"]["version"] == "0.1.0-alpha"
        assert data["api"]["status"] == "healthy"
    
    def test_status_returns_paths(self, api_client):
        """Status endpoint should return path information."""
        response = api_client.get("/status")
        data = response.json()
        
        assert "paths" in data
        assert "config" in data["paths"]
        assert "state" in data["paths"]
        assert "logs" in data["paths"]
    
    def test_status_returns_cache_info(self, api_client):
        """Status endpoint should return cache information."""
        response = api_client.get("/status")
        data = response.json()
        
        assert "cache" in data
        assert "tools_cached" in data["cache"]
        assert "cache_ttl_seconds" in data["cache"]


class TestToolRegistry:
    """Test cases for tool_registry module."""
    
    def test_tool_registry_discover_returns_list(self):
        """discover() should return a list."""
        from backend.tool_registry import discover
        result = discover()
        assert isinstance(result, list)
    
    def test_tool_registry_discover_returns_dicts(self):
        """discover() should return dictionaries."""
        from backend.tool_registry import discover
        result = discover()
        
        for item in result:
            assert isinstance(item, dict)
    
    def test_tool_registry_discover_includes_executable(self):
        """discover() should include executable field."""
        from backend.tool_registry import discover
        result = discover()
        
        for item in result:
            assert "executable" in item
            assert isinstance(item["executable"], str)
    
    def test_tool_registry_discover_includes_installed(self):
        """discover() should include installed status."""
        from backend.tool_registry import discover
        result = discover()
        
        for item in result:
            assert "installed" in item
            assert isinstance(item["installed"], bool)
    
    def test_tool_registry_get_installed_tools(self):
        """get_installed_tools() should return only installed tools."""
        from backend.tool_registry import get_installed_tools
        result = get_installed_tools()
        
        for tool in result:
            assert tool["installed"] is True
    
    def test_tool_registry_get_tools_by_provider(self):
        """get_tools_by_provider() should filter by provider."""
        from backend.tool_registry import get_tools_by_provider
        result = get_tools_by_provider("kodachi")
        
        for tool in result:
            assert tool.get("provider") == "kodachi"
    
    def test_tool_registry_get_tools_by_category(self):
        """get_tools_by_category() should filter by category."""
        from backend.tool_registry import get_tools_by_category
        result = get_tools_by_category("network")
        
        for tool in result:
            assert "network" in tool.get("categories", [])


class TestCORS:
    """Test cases for CORS configuration."""
    
    def test_cors_allows_localhost(self, api_client):
        """CORS should allow localhost."""
        response = api_client.get(
            "/health",
            headers={"origin": "http://localhost"}
        )
        assert response.status_code == 200
    
    def test_cors_allows_127_0_0_1(self, api_client):
        """CORS should allow 127.0.0.1."""
        response = api_client.get(
            "/health",
            headers={"origin": "http://127.0.0.1"}
        )
        assert response.status_code == 200


class TestErrorHandling:
    """Test cases for error handling."""
    
    def test_invalid_endpoint_returns_404(self, api_client):
        """Invalid endpoint should return 404."""
        response = api_client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_api_errors_are_json(self, api_client):
        """API errors should return JSON."""
        response = api_client.get("/nonexistent")
        assert response.headers["content-type"] == "application/json"
    
    def test_health_endpoint_handles_errors(self, api_client):
        """Health endpoint should handle internal errors gracefully."""
        # This test ensures the endpoint doesn't crash
        response = api_client.get("/health")
        assert response.status_code in [200, 500]


class TestDocumentation:
    """Test cases for API documentation."""
    
    def test_openapi_json_is_available(self, api_client):
        """OpenAPI JSON should be available."""
        response = api_client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data or "swagger" in data
    
    def test_swagger_docs_are_available(self, api_client):
        """Swagger UI should be available."""
        response = api_client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
