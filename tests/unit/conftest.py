import os
import pytest


@pytest.fixture(autouse=True)
def set_test_env():
    """Force SQLite in-memory for unit tests — no real DB needed."""
    original = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    yield
    if original is None:
        os.environ.pop("DATABASE_URL", None)
    else:
        os.environ["DATABASE_URL"] = original
