from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthcheck() -> None:
    response = client.get("/api/v1/health/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_default_admin_can_login() -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@geoinventario.local", "password": "admin123"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_inventory_summary_requires_authenticated_user() -> None:
    response = client.get("/api/v1/inventory/summary")

    assert response.status_code == 401
