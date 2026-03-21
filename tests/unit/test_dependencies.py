from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from src import dependencies


@pytest.mark.asyncio
async def test_get_current_user_without_credentials_raises_401():
    with pytest.raises(HTTPException) as exc:
        await dependencies.get_current_user(credentials=None)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token_raises_401(mocker):
    mocker.patch("src.dependencies.decode_access_token", return_value=None)

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad-token")

    with pytest.raises(HTTPException) as exc:
        await dependencies.get_current_user(credentials=credentials)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid or expired token"


@pytest.mark.asyncio
async def test_get_current_user_without_sub_raises_401(mocker):
    mocker.patch("src.dependencies.decode_access_token", return_value={"iat": 123})

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")

    with pytest.raises(HTTPException) as exc:
        await dependencies.get_current_user(credentials=credentials)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token payload"


@pytest.mark.asyncio
async def test_get_current_user_user_not_found_raises_401(mocker):
    mocker.patch("src.dependencies.decode_access_token", return_value={"sub": "ghost"})
    mocker.patch(
        "src.dependencies.get_user_by_username", new=AsyncMock(return_value=None)
    )

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")

    with pytest.raises(HTTPException) as exc:
        await dependencies.get_current_user(credentials=credentials)

    assert exc.value.status_code == 401
    assert exc.value.detail == "User not found"


@pytest.mark.asyncio
async def test_get_current_user_success(mocker):
    mocker.patch("src.dependencies.decode_access_token", return_value={"sub": "alice"})
    mocker.patch(
        "src.dependencies.get_user_by_username",
        new=AsyncMock(return_value={"id": 1, "username": "alice"}),
    )

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")
    user = await dependencies.get_current_user(credentials=credentials)

    assert user["username"] == "alice"
