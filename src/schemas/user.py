from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=5, max_length=128)


class TokenRequest(BaseModel):
    username: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=5, max_length=128)
