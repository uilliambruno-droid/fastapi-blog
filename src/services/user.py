from src.config import settings
from src.database import database
from src.exceptions import ConflictError, UnauthorizedError
from src.models.user import users
from src.schemas.user import UserCreate
from src.utils.auth import hash_password, verify_password


async def _fetch_user_by_username(username: str):
    return await database.fetch_one(users.select().where(users.c.username == username))


async def get_user_by_username(username: str):
    return await _fetch_user_by_username(username)


async def create_user(user: UserCreate):
    existing = await _fetch_user_by_username(user.username)
    if existing:
        raise ConflictError("Username already taken")
    query = users.insert().values(
        username=user.username,
        hashed_password=hash_password(user.password),
    )
    user_id = await database.execute(query)
    return await database.fetch_one(users.select().where(users.c.id == user_id))


async def authenticate_user(username: str, password: str):
    user = await _fetch_user_by_username(username)
    if user is None or not verify_password(password, user["hashed_password"]):
        raise UnauthorizedError("Incorrect username or password")
    return user


async def seed_admin():
    existing = await _fetch_user_by_username(settings.seed_admin_username)
    if existing is None:
        query = users.insert().values(
            username=settings.seed_admin_username,
            hashed_password=hash_password(settings.seed_admin_password),
        )
        await database.execute(query)
