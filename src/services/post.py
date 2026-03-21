from fastapi import HTTPException, status

from src.database import database
from src.models.post import posts
from src.schemas.post import PostCreate, PostUpdate


def _is_admin(current_user) -> bool:
    return current_user["username"] == "admin"


def _ensure_post_owner_or_admin(post, current_user):
    if post["author_id"] != current_user["id"] and not _is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to modify this post",
        )


def _post_by_id_query(post_id: int):
    return posts.select().where(posts.c.id == post_id)


async def _fetch_post_or_404(post_id: int, detail: str = "Post not found"):
    post = await database.fetch_one(_post_by_id_query(post_id))
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )
    return post


async def list_posts(published: bool | None = None, skip: int = 0, limit: int = 10):
    query = posts.select().offset(skip).limit(limit)
    if published is not None:
        query = query.where(posts.c.published == published)
    return await database.fetch_all(query)


async def get_post_by_id(post_id: int):
    return await _fetch_post_or_404(post_id)


async def create_new_post(post: PostCreate, current_user):
    query = posts.insert().values(**post.model_dump(), author_id=current_user["id"])
    post_id = await database.execute(query)
    return await _fetch_post_or_404(post_id, detail="Post not found after create")


async def patch_post(post_id: int, post: PostUpdate, current_user):
    values_to_update = post.model_dump(exclude_unset=True)
    existing_post = await _fetch_post_or_404(post_id)
    _ensure_post_owner_or_admin(existing_post, current_user)

    if values_to_update:
        update_query = (
            posts.update().where(posts.c.id == post_id).values(**values_to_update)
        )
        await database.execute(update_query)
    return await _fetch_post_or_404(post_id, detail="Post not found after update")


async def remove_post(post_id: int, current_user):
    existing_post = await _fetch_post_or_404(post_id)
    _ensure_post_owner_or_admin(existing_post, current_user)

    delete_query = posts.delete().where(posts.c.id == post_id)
    await database.execute(delete_query)
