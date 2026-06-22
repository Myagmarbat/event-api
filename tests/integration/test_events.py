"""Integration tests for event API endpoints."""
from fastapi.testclient import TestClient
from app.main import app


def _client():
    # Use per-test client context to avoid leakage across tests.
    return TestClient(app)


def test_health():
    """Test health check endpoint."""
    with _client() as client:
        response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_create_event():
    """Test creating a new event."""
    payload = {"event_type": "signup", "user_id": "123"}
    with _client() as client:
        response = client.post("/events", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["event_type"] == payload["event_type"]
    assert data["user_id"] == payload["user_id"]
    assert "id" in data
    assert "created_at" in data


def test_create_event_empty_event_type():
    with _client() as client:
        response = client.post("/events", json={"event_type": "", "user_id": "123"})
    assert response.status_code == 422


def test_create_event_empty_user_id():
    with _client() as client:
        response = client.post("/events", json={"event_type": "signup", "user_id": ""})
    assert response.status_code == 422


def test_create_event_missing_event_type():
    with _client() as client:
        response = client.post("/events", json={"user_id": "123"})
    assert response.status_code == 422


def test_create_event_missing_user_id():
    with _client() as client:
        response = client.post("/events", json={"event_type": "signup"})
    assert response.status_code == 422


def test_create_event_wrong_types():
    with _client() as client:
        response = client.post("/events", json={"event_type": 123, "user_id": True})
    assert response.status_code == 422


def test_get_event_flow():
    """Test creating and retrieving an event."""
    with _client() as client:
        created = client.post("/events", json={"event_type": "login", "user_id": "456"})
        assert created.status_code == 201
        event_id = created.json()["id"]

        response = client.get(f"/events/{event_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == event_id
    assert body["event_type"] == "login"
    assert body["user_id"] == "456"


def test_get_event_not_found():
    with _client() as client:
        response = client.get("/events/nonexistent-id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_events_contains_created_item():
    with _client() as client:
        created = client.post("/events", json={"event_type": "list_test", "user_id": "u1"})
        assert created.status_code == 201
        created_id = created.json()["id"]

        response = client.get("/events")

    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert any(item["id"] == created_id for item in items)


def test_delete_event():
    with _client() as client:
        created = client.post("/events", json={"event_type": "delete_test", "user_id": "789"})
        assert created.status_code == 201
        event_id = created.json()["id"]

        deleted = client.delete(f"/events/{event_id}")
        fetched = client.get(f"/events/{event_id}")

    assert deleted.status_code == 204
    assert fetched.status_code == 404


def test_delete_event_not_found():
    with _client() as client:
        response = client.delete("/events/nonexistent-id")
    assert response.status_code == 404