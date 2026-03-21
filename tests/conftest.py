import sys
import uuid
from pathlib import Path

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import src.models.post  # noqa: F401, E402
import src.models.user  # noqa: F401, E402
from src.database import database, engine, metadata  # noqa: E402
from src.main import app  # noqa: E402
from src.models.post import posts  # noqa: E402
from src.models.user import users  # noqa: E402
from src.services.user import seed_admin  # noqa: E402


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    metadata.drop_all(engine)
    metadata.create_all(engine)
    await database.connect()
    await seed_admin()
    yield
    await database.disconnect()


@pytest_asyncio.fixture(autouse=True)
async def cleanup_tables():
    await database.execute(posts.delete())
    await database.execute(users.delete().where(users.c.username != "admin"))
    yield


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client


@pytest_asyncio.fixture
async def admin_token(client):
    response = await client.post(
        "/auth/token",
        json={"username": "admin", "password": "admin"},
    )
    response.raise_for_status()
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def unique_user_payload():
    suffix = uuid.uuid4().hex[:8]
    return {
        "username": f"user_{suffix}",
        "password": "password123",
    }
