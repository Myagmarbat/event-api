"""Integration checks against the deployed stage API."""

import os
import time
import uuid

import httpx


def _base_url() -> str:
    value = os.environ.get("STAGE_BASE_URL")
    if not value:
        raise RuntimeError("STAGE_BASE_URL is required")
    return value.rstrip("/")


def _wait_for_health(timeout_seconds: int = 180, interval_seconds: int = 5) \
        -> httpx.Response:
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        try:
            response = httpx.get(f"{_base_url()}/health", timeout=10)
            if response.status_code == 200:
                return response
            last_error = AssertionError(
                f"unexpected status {response.status_code}: {response.text}"
            )
        except httpx.HTTPError as exc:
            last_error = exc

        time.sleep(interval_seconds)

    raise AssertionError("stage API never became healthy") from last_error


def test_stage_health():
    response = _wait_for_health()

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_stage_create_get_delete_event():
    _wait_for_health()
    user_id = f"stage-test-{uuid.uuid4()}"
    payload = {"event_type": "stage_smoke_test", "user_id": user_id}

    with httpx.Client(base_url=_base_url(), timeout=10) as client:
        created = client.post("/events", json=payload)
        assert created.status_code == 201

        event = created.json()
        assert event["event_type"] == payload["event_type"]
        assert event["user_id"] == payload["user_id"]

        fetched = client.get(f"/events/{event['id']}")
        assert fetched.status_code == 200
        assert fetched.json()["id"] == event["id"]

        deleted = client.delete(f"/events/{event['id']}")
        assert deleted.status_code == 204

        missing = client.get(f"/events/{event['id']}")
        assert missing.status_code == 404
