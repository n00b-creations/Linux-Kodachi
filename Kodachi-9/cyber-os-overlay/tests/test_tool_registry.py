import os
import pytest

from backend import tool_registry


def test_tool_registry_discover(tmp_path, monkeypatch):
    # create a fake providers dir
    pdir = tmp_path / "providers"
    pdir.mkdir()
    f = pdir / "prov.yaml"
    f.write_text("tools:\n  - id: testcmd\n    name: TestCmd\n    executable: echo\n    category: misc\n")

    tr = tool_registry.ToolRegistry(providers_dir=str(pdir))
    results = tr.discover()
    assert isinstance(results, list)
    assert any(r.get('id') == 'testcmd' for r in results)
