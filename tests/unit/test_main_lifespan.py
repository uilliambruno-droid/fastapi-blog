from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI

from src.main import lifespan


@pytest.mark.asyncio
async def test_lifespan_with_seed_enabled(mocker):
    connect_mock = mocker.patch("src.main.database.connect", new=AsyncMock())
    disconnect_mock = mocker.patch("src.main.database.disconnect", new=AsyncMock())
    create_all_mock = mocker.patch("src.main.metadata.create_all")
    seed_admin_mock = mocker.patch("src.services.user.seed_admin", new=AsyncMock())
    mocker.patch("src.main.settings.seed_admin_enabled", True)

    async with lifespan(FastAPI()):
        pass

    connect_mock.assert_called_once()
    create_all_mock.assert_called_once()
    seed_admin_mock.assert_called_once()
    disconnect_mock.assert_called_once()


@pytest.mark.asyncio
async def test_lifespan_with_seed_disabled(mocker):
    connect_mock = mocker.patch("src.main.database.connect", new=AsyncMock())
    disconnect_mock = mocker.patch("src.main.database.disconnect", new=AsyncMock())
    create_all_mock = mocker.patch("src.main.metadata.create_all")
    seed_admin_mock = mocker.patch("src.services.user.seed_admin", new=AsyncMock())
    mocker.patch("src.main.settings.seed_admin_enabled", False)

    async with lifespan(FastAPI()):
        pass

    connect_mock.assert_called_once()
    create_all_mock.assert_called_once()
    seed_admin_mock.assert_not_called()
    disconnect_mock.assert_called_once()
