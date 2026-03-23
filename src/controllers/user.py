from fastapi import APIRouter, Depends, HTTPException, status

from src.dependencies import get_current_user
from src.exceptions import ConflictError, UnauthorizedError
from src.schemas.token import Token
from src.schemas.user import TokenRequest, UserCreate
from src.services.user import authenticate_user, create_user
from src.utils.auth import create_access_token
from src.views.user import UserOut

router = APIRouter()
protected_router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/auth/token", response_model=Token)
async def login(credentials: TokenRequest):
    try:
        user = await authenticate_user(credentials.username, credentials.password)
    except UnauthorizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}


@protected_router.post(
    "/users/", response_model=UserOut, status_code=status.HTTP_201_CREATED
)
async def register_user(user: UserCreate):
    try:
        return await create_user(user)
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.detail)
