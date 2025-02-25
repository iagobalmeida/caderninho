import pytest
from fastapi.testclient import TestClient

from src import db
from src.app import app
from src.scripts import seed


@pytest.fixture(autouse=True, scope="session")
def setup_test_db():
    db.reset()
    seed.main()
    yield


@pytest.fixture
def client():
    test_client = TestClient(app)
    with db.init_session():
        yield test_client
