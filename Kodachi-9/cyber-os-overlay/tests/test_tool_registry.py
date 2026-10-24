from pathlib import Path

from backend import tool_registry


def test_default_provider_directory_is_inside_overlay():
    expected = Path(tool_registry.__file__).resolve().parents[1] / "integrations" / "tool-registry" / "providers"
    assert Path(tool_registry.PROVIDERS_DIR) == expected
    assert expected.is_dir()

    registry = tool_registry.ToolRegistry()
    assert "git" in {tool["id"] for tool in registry.discover()} 
