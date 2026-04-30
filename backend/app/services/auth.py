from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, RedisStrategy
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.redis import get_redis_client
from app.db.user import get_user_db
from app.models.user import User
from app.schemas.auth import LoginRequest

settings = get_settings()


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.auth_secret
    verification_token_secret = settings.auth_secret


async def get_user_manager(user_db=Depends(get_user_db)) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)


class SlidingRedisStrategy(RedisStrategy[User, int]):

    def _user_tokens_key(self, user_id: int) -> str:
        return f"max_agent_user_tokens:{user_id}"

    async def write_token(self, user: User) -> str:
        token = await super().write_token(user)
        user_key = self._user_tokens_key(user.id)
        await self.redis.sadd(user_key, token)
        if self.lifetime_seconds is not None:
            await self.redis.expire(user_key, self.lifetime_seconds)
        return token

    async def read_token(self, token: str | None, user_manager: BaseUserManager[User, int]) -> User | None:
        user = await super().read_token(token, user_manager)
        if user is not None and token is not None and self.lifetime_seconds is not None:
            await self.redis.expire(f"{self.key_prefix}{token}", self.lifetime_seconds)
        return user

    async def destroy_token(self, token: str, user: User) -> None:
        await super().destroy_token(token, user)
        user_key = self._user_tokens_key(user.id)
        await self.redis.srem(user_key, token)
        remaining = await self.redis.scard(user_key)
        if remaining == 0:
            await self.redis.delete(user_key)
        elif self.lifetime_seconds is not None:
            await self.redis.expire(user_key, self.lifetime_seconds)

    async def destroy_user_tokens(self, user_id: int) -> None:
        user_key = self._user_tokens_key(user_id)
        tokens = await self.redis.smembers(user_key)
        if tokens:
            token_keys = [
                f"{self.key_prefix}{t.decode() if isinstance(t, bytes) else t}"
                for t in tokens
            ]
            await self.redis.delete(*token_keys)
        await self.redis.delete(user_key)


bearer_transport = BearerTransport(tokenUrl=f"{settings.api_prefix}/auth/login")


async def get_redis_strategy() -> SlidingRedisStrategy:
    return SlidingRedisStrategy(
        get_redis_client(),
        lifetime_seconds=settings.access_token_ttl_seconds,
        key_prefix="max_agent_token:",
    )


auth_backend = AuthenticationBackend(
    name="redis",
    transport=bearer_transport,
    get_strategy=get_redis_strategy,
)
fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])
current_active_user = fastapi_users.current_user(active=True)


async def authenticate_user(
    payload: LoginRequest,
    session: AsyncSession,
    user_manager: UserManager,
) -> User | None:
    statement = select(User).where(
        or_(User.username == payload.username, User.email == payload.username)
    )
    user = await session.scalar(statement)
    if user is None:
        user_manager.password_helper.hash(payload.password)
        return None

    verified, updated_password_hash = user_manager.password_helper.verify_and_update(
        payload.password,
        user.hashed_password,
    )
    if not verified or not user.is_active:
        return None

    if updated_password_hash is not None:
        user.hashed_password = updated_password_hash
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user
