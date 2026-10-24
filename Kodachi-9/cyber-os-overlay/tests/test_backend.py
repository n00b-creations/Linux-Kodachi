import pytest

from backend.tool_registry import ToolRegistry


def test_registry_discovers_provider_metadata(tmp_path, monkeypatch):
    providers = tmp_path / "providers"
    providers.mkdir()
    (providers / "sample.yaml").write_text(
        "tools:\n  - id: sample\n    name: Sample Tool\n    executable: sample-tool\n    category: testing\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("backend.tool_registry.shutil.which", lambda name: "/usr/bin/sample-tool")

    result = ToolRegistry(providers_dir=str(providers)).discover()

    assert result == [
        {
            "id": "sample",
            "name": "Sample Tool",
            "executable": "sample-tool",
            "available": True,
            "category": "testing",
            "source_file": "sample.yaml",
        }
    ]


def test_registry_rejects_missing_provider_directory(tmp_path):
    with pytest.raises(FileNotFoundError, match="Providers dir not found"):
        ToolRegistry(providers_dir=str(tmp_path / "does-not-exist"))
