from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine

from src import db
from src.app import app
from src.scripts import seed

DB_RESTARTED = False


@pytest.fixture
def mock_session():
    engine = create_engine("sqlite:///test.db", echo=False)
    """Cria um mock da sessão autenticada"""
    with Session(engine) as session:
        setattr(session, 'sessao_autenticada', MagicMock())
        session.sessao_autenticada.administrador = False
        session.sessao_autenticada.dono = False
        session.sessao_autenticada.organizacao_id = 1
        session.sessao_autenticada.id = 1
        yield session
    session.close()


@pytest.fixture(autouse=True, scope="session")
def setup_test_db():
    db.reset()
    seed.main()
    yield


@pytest.fixture
def client():
    test_client = TestClient(app)
    yield test_client
