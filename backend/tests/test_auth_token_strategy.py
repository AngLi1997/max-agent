from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.auth import SlidingRedisStrategy


class FakeRedis:
    """最小化 Redis mock，只实现 token 索引需要的方法。"""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}
        self._sets: dict[str, set[str]] = {}

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        self._store[key] = value

    async def get(self, key: str) -> str | None:
        return self._store.get(key)

    async def delete(self, *keys: str) -> None:
        for k in keys:
            self._store.pop(k, None)
            self._sets.pop(k, None)

    async def sadd(self, key: str, *values: str) -> None:
        self._sets.setdefault(key, set()).update(values)

    async def srem(self, key: str, *values: str) -> None:
        if key in self._sets:
            self._sets[key] -= set(values)

    async def smembers(self, key: str) -> set[str]:
        return self._sets.get(key, set())

    async def scard(self, key: str) -> int:
        return len(self._sets.get(key, set()))

    async def expire(self, key: str, seconds: int) -> None:
        pass  # TTL 不影响单元测试逻辑


def _make_strategy(redis: FakeRedis) -> SlidingRedisStrategy:
    return SlidingRedisStrategy(
        redis,  # type: ignore[arg-type]
        lifetime_seconds=3600,
        key_prefix="max_agent_token:",
    )


def _make_user(user_id: int = 1) -> MagicMock:
    user = MagicMock()
    user.id = user_id
    return user


@pytest.mark.asyncio
async def test_write_token_adds_to_user_set() -> None:
    redis = FakeRedis()
    strategy = _make_strategy(redis)
    user = _make_user(42)

    token = await strategy.write_token(user)

    assert token in await redis.smembers("max_agent_user_tokens:42")


@pytest.mark.asyncio
async def test_destroy_token_removes_from_user_set() -> None:
    redis = FakeRedis()
    strategy = _make_strategy(redis)
    user = _make_user(42)

    token = await strategy.write_token(user)
    await strategy.destroy_token(token, user)

    assert token not in await redis.smembers("max_agent_user_tokens:42")


@pytest.mark.asyncio
async def test_destroy_user_tokens_clears_all() -> None:
    redis = FakeRedis()
    strategy = _make_strategy(redis)
    user = _make_user(42)

    t1 = await strategy.write_token(user)
    t2 = await strategy.write_token(user)

    await strategy.destroy_user_tokens(42)

    assert await redis.smembers("max_agent_user_tokens:42") == set()
    assert await redis.get(f"max_agent_token:{t1}") is None
    assert await redis.get(f"max_agent_token:{t2}") is None
