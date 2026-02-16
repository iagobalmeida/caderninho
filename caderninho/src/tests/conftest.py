import asyncio

import pytest_asyncio
from app import app

from caderninho.src import db
from caderninho.src.scripts import seed


@pytest_asyncio.fixture(autouse=True, scope="session")
def event_loop():
    """Cria um único loop para toda a sessão de testes"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True, scope="session")
async def setup_test_db():
    await db.reset()
    await seed.main()
    yield


@pytest_asyncio.fixture
async def db_session():
    async with db.init_session() as db_session:
        yield db_session


@pytest_asyncio.fixture
async def client(db_session):
    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as ac:
        yield ac
