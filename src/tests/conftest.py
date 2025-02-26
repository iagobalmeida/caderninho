import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from src import db
from src.app import app
from src.scripts import seed


@pytest_asyncio.fixture(autouse=True, scope="session")
async def setup_test_db():
    await db.reset()
    await seed.main()
    yield


@pytest_asyncio.fixture
async def client():
    from httpx import ASGITransport, AsyncClient
    async with db.init_session():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as ac:
            yield ac
