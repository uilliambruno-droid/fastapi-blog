from fastapi import APIRouter, Depends, Query, Response, status

from src.dependencies import get_current_user
from src.schemas.post import PostCreate, PostUpdate
from src.services.post import (
    create_new_post,
    get_post_by_id,
    list_posts,
    patch_post,
    remove_post,
)
from src.views.post import PostOut

router = APIRouter(prefix="/posts")
protected_router = APIRouter(
    prefix="/posts",
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=list[PostOut])
async def read_posts(
    published: bool | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):
    return await list_posts(published=published, skip=skip, limit=limit)


@router.get("/{post_id}", response_model=PostOut)
async def get_post(post_id: int):
    return await get_post_by_id(post_id)


@protected_router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, current_user=Depends(get_current_user)):
    return await create_new_post(post, current_user)


@protected_router.patch("/{post_id}", response_model=PostOut)
async def update_post(
    post_id: int,
    post: PostUpdate,
    current_user=Depends(get_current_user),
):
    return await patch_post(post_id, post, current_user)


@protected_router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, current_user=Depends(get_current_user)):
    await remove_post(post_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
