from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_create_event():
    response = client.post("/events", json={
        "event_type": "signup",
        "user_id": "123"
    })

    assert response.status_code == 201
    assert response.json()["event_type"] == "signup"


def test_get_event_flow():
    created = client.post("/events", json={
        "event_type": "signup",
        "user_id": "123"
    })

    event_id = created.json()["id"]

    response = client.get(f"/events/{event_id}")
    assert response.status_code == 200