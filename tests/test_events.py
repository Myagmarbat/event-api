"""Integration tests for event API endpoints."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_event():
    """Test creating a new event."""
    response = client.post("/events", json={
        "event_type": "signup",
        "user_id": "123"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["event_type"] == "signup"
    assert data["user_id"] == "123"
    assert "id" in data
    assert "created_at" in data


def test_create_event_empty_event_type():
    """Test creating event with empty event_type."""
    response = client.post("/events", json={
        "event_type": "",
        "user_id": "123"
    })
    assert response.status_code == 422  # Validation error


def test_create_event_empty_user_id():
    """Test creating event with empty user_id."""
    response = client.post("/events", json={
        "event_type": "signup",
        "user_id": ""
    })
    assert response.status_code == 422  # Validation error


def test_get_event_flow():
    """Test creating and retrieving an event."""
    # Create event
    created = client.post("/events", json={
        "event_type": "login",
        "user_id": "456"
    })
    assert created.status_code == 201

    event_id = created.json()["id"]

    # Retrieve event
    response = client.get(f"/events/{event_id}")
    assert response.status_code == 200
    assert response.json()["id"] == event_id
    assert response.json()["event_type"] == "login"


def test_get_event_not_found():
    """Test retrieving non-existent event."""
    response = client.get("/events/nonexistent-id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_events():
    """Test listing all events."""
    response = client.get("/events")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_delete_event():
    """Test deleting an event."""
    # Create event
    created = client.post("/events", json={
        "event_type": "delete_test",
        "user_id": "789"
    })
    event_id = created.json()["id"]

    # Delete event
    response = client.delete(f"/events/{event_id}")
    assert response.status_code == 204

    # Verify it's deleted
    response = client.get(f"/events/{event_id}")
    assert response.status_code == 404


def test_delete_event_not_found():
    """Test deleting non-existent event."""
    response = client.delete("/events/nonexistent-id")
    assert response.status_code == 404
