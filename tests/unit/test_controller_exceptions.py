"""Unit tests for controller exception handling.

Verifies that each controller route correctly catches domain exceptions
(NotFoundError, ForbiddenError, ConflictError, UnauthorizedError) and
translates them into the expected HTTP status codes and JSON responses.
"""

from unittest.mock import AsyncMock, patch

import pytest

from src.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)

# ---------------------------------------------------------------------------
# Post controller
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_post_returns_404_on_not_found(client):
    with patch(
        "src.controllers.post.get_post_by_id",
        new=AsyncMock(side_effect=NotFoundError("Post not found")),
    ):
        response = await client.get("/posts/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


@pytest.mark.asyncio
async def test_create_post_returns_404_on_not_found(client, admin_token):
    with patch(
        "src.controllers.post.create_new_post",
        new=AsyncMock(side_effect=NotFoundError("Post not found after create")),
    ):
        response = await client.post(
            "/posts/",
            json={"title": "Test title", "content": "Some content", "published": True},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_post_returns_404_on_not_found(client, admin_token):
    with patch(
        "src.controllers.post.patch_post",
        new=AsyncMock(side_effect=NotFoundError("Post not found")),
    ):
        response = await client.patch(
            "/posts/999",
            json={"title": "new"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_post_returns_403_on_forbidden(client, admin_token):
    with patch(
        "src.controllers.post.patch_post",
        new=AsyncMock(
            side_effect=ForbiddenError("You are not allowed to modify this post")
        ),
    ):
        response = await client.patch(
            "/posts/1",
            json={"title": "steal"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert response.status_code == 403
    assert "not allowed" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_post_returns_404_on_not_found(client, admin_token):
    with patch(
        "src.controllers.post.remove_post",
        new=AsyncMock(side_effect=NotFoundError("Post not found")),
    ):
        response = await client.delete(
            "/posts/999",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_post_returns_403_on_forbidden(client, admin_token):
    with patch(
        "src.controllers.post.remove_post",
        new=AsyncMock(
            side_effect=ForbiddenError("You are not allowed to modify this post")
        ),
    ):
        response = await client.delete(
            "/posts/1",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert response.status_code == 403
    assert "not allowed" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# User controller
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_login_returns_401_on_invalid_credentials(client):
    with patch(
        "src.controllers.user.authenticate_user",
        new=AsyncMock(side_effect=UnauthorizedError("Incorrect username or password")),
    ):
        response = await client.post(
            "/auth/token",
            json={"username": "ghost", "password": "wrong"},
        )

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()
    assert response.headers.get("www-authenticate") == "Bearer"


@pytest.mark.asyncio
async def test_register_returns_409_on_conflict(client, admin_token):
    with patch(
        "src.controllers.user.create_user",
        new=AsyncMock(side_effect=ConflictError("Username already taken")),
    ):
        response = await client.post(
            "/users/",
            json={"username": "duplicate", "password": "12345"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert response.status_code == 409
    assert "already taken" in response.json()["detail"].lower()
