import os
from fastapi.testclient import TestClient

from Kodachi_9_cyber import startup_helper

# This test assumes the package isn't installed; we will import app directly
# Fallback to loading the module path where cyber_os_api lives

try:
    from Kodachi_9_cyber.backend.cyber_os_api import app
except Exception:
    from importlib import import_module
    mod = import_module('Kodachi-9.cyber-os-overlay.backend.cyber_os_api')
    app = mod.app

client = TestClient(app)


def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json().get('status') == 'ok'


def test_tools_monkeypatch(monkeypatch):
    # Monkeypatch the registry to return fake tools
    class FakeRegistry:
        def discover(self):
            return [{'id':'git','name':'Git','executable':'git','available':True}]
        def reload(self):
            pass

    # Replace the registry in the module
    import sys
    mod = sys.modules.get('Kodachi-9.cyber-os-overlay.backend.cyber_os_api')
    # Best-effort: patch by attribute if possible
    try:
        mod._registry = FakeRegistry()
    except Exception:
        pass

    r = client.get('/tools')
    assert r.status_code == 200
    assert 'tools' in r.json()
