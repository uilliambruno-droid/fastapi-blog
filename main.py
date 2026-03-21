from datetime import datetime, timezone
from threading import Lock
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="FastAPI Blog", description="A simple blog API", version="1.0.0")

# In-memory storage for blog posts (protected by a lock for thread safety)
_lock = Lock()
posts: dict[int, dict] = {}
next_id = 1


class PostCreate(BaseModel):
    title: str
    content: str
    author: str


class Post(BaseModel):
    id: int
    title: str
    content: str
    author: str
    created_at: datetime


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "message": "FastAPI Blog is running!"}


@app.get("/posts", response_model=List[Post], tags=["posts"])
def list_posts():
    with _lock:
        return list(posts.values())


@app.get("/posts/{post_id}", response_model=Post, tags=["posts"])
def get_post(post_id: int):
    with _lock:
        post = posts.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.post("/posts", response_model=Post, status_code=201, tags=["posts"])
def create_post(post_data: PostCreate):
    global next_id
    with _lock:
        post = Post(
            id=next_id,
            title=post_data.title,
            content=post_data.content,
            author=post_data.author,
            created_at=datetime.now(timezone.utc),
        )
        posts[next_id] = post.model_dump()
        next_id += 1
    return post


@app.delete("/posts/{post_id}", status_code=204, tags=["posts"])
def delete_post(post_id: int):
    with _lock:
        if post_id not in posts:
            raise HTTPException(status_code=404, detail="Post not found")
        del posts[post_id]
