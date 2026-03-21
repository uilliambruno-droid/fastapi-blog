from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from src.schemas.user import UserCreate
from src.services import user as user_service


@pytest.mark.asyncio
async def test_create_user_conflict_raises(mocker):
    mocker.patch(
        "src.services.user._fetch_user_by_username",
        new=AsyncMock(return_value={"id": 1, "username": "existing"}),
    )

    with pytest.raises(HTTPException) as exc:
        await user_service.create_user(
            UserCreate(username="existing", password="12345")
        )

    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_create_user_success(mocker):
    mocker.patch(
        "src.services.user._fetch_user_by_username",
        new=AsyncMock(return_value=None),
    )
    mocker.patch("src.services.user.hash_password", return_value="hashed-password")
    mocker.patch("src.services.user.database.execute", new=AsyncMock(return_value=10))
    mocker.patch(
        "src.services.user.database.fetch_one",
        new=AsyncMock(return_value={"id": 10, "username": "newuser"}),
    )

    result = await user_service.create_user(
        UserCreate(username="newuser", password="12345")
    )

    assert result["id"] == 10
    assert result["username"] == "newuser"


@pytest.mark.asyncio
async def test_authenticate_user_invalid_credentials(mocker):
    mocker.patch(
        "src.services.user._fetch_user_by_username",
        new=AsyncMock(return_value=None),
    )

    with pytest.raises(HTTPException) as exc:
        await user_service.authenticate_user("nouser", "12345")

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_authenticate_user_success(mocker):
    mocker.patch(
        "src.services.user._fetch_user_by_username",
        new=AsyncMock(
            return_value={"id": 1, "username": "alice", "hashed_password": "hashed"}
        ),
    )
    mocker.patch("src.services.user.verify_password", return_value=True)

    user = await user_service.authenticate_user("alice", "12345")

    assert user["username"] == "alice"
