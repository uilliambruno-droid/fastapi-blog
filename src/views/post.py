import datetime

from pydantic import BaseModel


class PostOut(BaseModel):
    id: int
    title: str
    content: str
    published: bool = False
    author_id: int
    date: datetime.datetime
