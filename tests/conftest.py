import os
import pytest

@pytest.fixture(autouse=True)
def set_test_env():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"