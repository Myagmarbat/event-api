"""Integration tests for event API endpoints."""

import logging
import pytest
from dotenv import load_dotenv

load_dotenv()

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app.db import Base, init_engine  # noqa: E402
import app.db as _db  # noqa: E402

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def clean_db():
    """Drop and recreate all tables before each test for a clean slate."""
    logger.info("Setting up test database...")
    init_engine()
    Base.metadata.drop_all(bind=_db.engine)
    Base.metadata.create_all(bind=_db.engine)
    yield
    logger.info("Tearing down test database...")
    Base.metadata.drop_all(bind=_db.engine)
    Base.metadata.create_all(bind=_db.engine)


def _client():
    return TestClient(app)


def test_health():
    logger.info("Running test_health")
    with _client() as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    logger.info("test_health passed")


def test_create_event():
    logger.info("Running test_create_event")
    payload = {"event_type": "signup", "user_id": "123"}
    with _client() as client:
        response = client.post("/events", json=payload)
    logger.info(f"Response status: {response.status_code}")
    assert response.status_code == 201
    data = response.json()
    assert data["event_type"] == payload["event_type"]
    assert data["user_id"] == payload["user_id"]
    assert "id" in data
    assert "created_at" in data
    logger.info(f"Created event: {data['id']}")


# ... rest of tests unchanged
