from contextlib import asynccontextmanager

from fastapi import FastAPI

import src.models.post  # noqa: F401
import src.models.user  # noqa: F401
from src.config import settings
from src.controllers import post, user
from src.database import database, engine, metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    metadata.create_all(engine)

    from src.services.user import seed_admin

    if settings.seed_admin_enabled:
        await seed_admin()

    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.include_router(post.router)
app.include_router(post.protected_router)
app.include_router(user.router)
app.include_router(user.protected_router)
