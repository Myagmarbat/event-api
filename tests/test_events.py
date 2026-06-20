from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_create_event():
    response = client.post(
        "/events",
        json={
            "event_type": "signup",
            "user_id": "123"
        }
    )
    assert response.status_code == 201
    body = response.json()
    assert body["event_type"] == "signup"

def test_invalid_event():
    response = client.post(
        "/events",
        json={}
    )

    assert response.status_code == 422

def test_get_event():
    create = client.post(
        "/events",
        json={
            "event_type": "signup",
            "user_id": "123"
        }
    )
    event_id = create.json()["id"]
    response = client.get(f"/events/{event_id}")
    assert response.status_code == 200

def test_event_not_found():
    response = client.get("/events/bad-id")
    assert response.status_code == 404

def test_delete_event():
    create = client.post(
        "/events",
        json={
            "event_type": "signup",
            "user_id": "123"
        }
    )
    event_id = create.json()["id"]
    response = client.delete(
        f"/events/{event_id}"
    )
    assert response.status_code == 200