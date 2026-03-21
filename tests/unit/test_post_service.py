from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from src.schemas.post import PostUpdate
from src.services import post as post_service


@pytest.mark.asyncio
async def test_get_post_by_id_not_found(mocker):
    mocker.patch(
        "src.services.post.database.fetch_one", new=AsyncMock(return_value=None)
    )

    with pytest.raises(HTTPException) as exc:
        await post_service.get_post_by_id(999)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_patch_post_without_changes_returns_current(mocker):
    mocker.patch(
        "src.services.post._fetch_post_or_404",
        new=AsyncMock(
            side_effect=[
                {"id": 1, "title": "same", "author_id": 10},
                {"id": 1, "title": "same", "author_id": 10},
            ]
        ),
    )
    execute_mock = mocker.patch("src.services.post.database.execute", new=AsyncMock())

    result = await post_service.patch_post(
        1,
        PostUpdate(),
        current_user={"id": 10, "username": "owner"},
    )

    execute_mock.assert_not_called()
    assert result["id"] == 1


@pytest.mark.asyncio
async def test_remove_post_executes_delete(mocker):
    mocker.patch(
        "src.services.post._fetch_post_or_404",
        new=AsyncMock(return_value={"id": 1, "author_id": 5}),
    )
    execute_mock = mocker.patch("src.services.post.database.execute", new=AsyncMock())

    await post_service.remove_post(1, current_user={"id": 5, "username": "owner"})

    execute_mock.assert_called_once()


@pytest.mark.asyncio
async def test_patch_post_forbidden_for_non_owner(mocker):
    mocker.patch(
        "src.services.post._fetch_post_or_404",
        new=AsyncMock(return_value={"id": 2, "author_id": 1}),
    )

    with pytest.raises(HTTPException) as exc:
        await post_service.patch_post(
            2,
            PostUpdate(title="new"),
            current_user={"id": 99, "username": "intruder"},
        )

    assert exc.value.status_code == 403
