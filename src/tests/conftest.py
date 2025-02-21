import pytest
from fastapi.testclient import TestClient

from src.app import app


@pytest.fixture
def client():
    test_client = TestClient(app)
    yield test_client
