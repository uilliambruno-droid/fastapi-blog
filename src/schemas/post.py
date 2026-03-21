from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    content: str = Field(min_length=1)
    published: bool = False


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    content: str | None = Field(default=None, min_length=1)
    published: bool | None = None
