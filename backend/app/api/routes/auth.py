from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db_session
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.user import CurrentUserResponse
from app.services.auth import (
    SlidingRedisStrategy,
    authenticate_user,
    current_active_user,
    get_redis_strategy,
    get_user_manager,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def get_bearer_token(authorization: Annotated[str | None, Header()] = None) -> str:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")
    return authorization[7:]


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
    user_manager=Depends(get_user_manager),
    strategy: SlidingRedisStrategy = Depends(get_redis_strategy),
) -> LoginResponse:
    user = await authenticate_user(payload, session, user_manager)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名或密码错误")

    token = await strategy.write_token(user)
    return LoginResponse(token=token, username=user.username)


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> CurrentUserResponse:
    full_user = await session.scalar(
        select(User).options(selectinload(User.roles)).where(User.id == user.id)
    )
    role_name = full_user.roles[0].name if full_user and full_user.roles else ""
    return CurrentUserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        avatar=user.avatar,
        role=role_name,
    )


@router.post("/logout")
async def logout(
    token: str = Depends(get_bearer_token),
    user: User = Depends(current_active_user),
    strategy: SlidingRedisStrategy = Depends(get_redis_strategy),
) -> dict[str, str]:
    await strategy.destroy_token(token, user)
    return {"message": "退出成功"}
