from contextlib import asynccontextmanager

from fastapi import FastAPI

import src.models.post  # noqa: F401
import src.models.user  # noqa: F401
from src.config import settings
from src.controllers import post, user
from src.database import database, engine, metadata
from src.middleware import (
    RequestLoggerMiddleware,
    SecurityHeadersMiddleware,
    setup_cors,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    metadata.create_all(engine)

    from src.services.user import seed_admin

    if settings.seed_admin_enabled:
        await seed_admin()

    yield
    await database.disconnect()


servers = [
    {"url": "http://localhost:8000", "description": "Development server"},
    {
        "url": "https://fastapi-blog-jrf4.onrender.com",
        "description": "Production server",
    },
]

app = FastAPI(
    title="FastAPI Blog",
    summary="A simple blog API built with FastAPI",
    description="This API allows you to create, read, update, and delete blog posts. It also includes user"
    " authentication and authorization features.",
    version="1.0.0",
    servers=servers,
    lifespan=lifespan,
)

# Setup middleware stack (order matters: last added is first in the chain)
setup_cors(app)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggerMiddleware)

# Include routers
app.include_router(post.router, tags=["Posts"])
app.include_router(post.protected_router, tags=["Posts"])
app.include_router(user.router, tags=["Users"])
app.include_router(user.protected_router, tags=["Users"])
