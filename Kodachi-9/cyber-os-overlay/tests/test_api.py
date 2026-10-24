from fastapi.testclient import TestClient

from backend.cyber_os_api import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_system_returns_resource_totals():
    response = client.get("/system")
    assert response.status_code == 200
    data = response.json()
    assert {"cpu_count", "memory_total", "disk_root", "prefix"} <= data.keys()


def test_tools_returns_a_tools_list():
    response = client.get("/tools")
    assert response.status_code == 200
    assert isinstance(response.json().get("tools"), list)


def test_reload_registry_rejects_non_loopback_client():
    response = client.post("/admin/reload-registry")
    assert response.status_code == 403
