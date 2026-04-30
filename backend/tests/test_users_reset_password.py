from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.routes import users as users_routes
from app.models.user import User


def _make_target(user_id: int = 10, is_builtin: bool = False) -> User:
    user = User(
        id=user_id,
        username="editor",
        email="editor@example.com",
        hashed_password="old_hash",
        is_active=True,
        is_superuser=False,
        is_verified=True,
        avatar="",
        status="active",
        is_builtin=is_builtin,
        must_change_password=False,
    )
    return user


def _make_actor() -> SimpleNamespace:
    return SimpleNamespace(id=1, username="admin", is_superuser=True)


def _make_session(target: User | None) -> MagicMock:
    session = MagicMock()
    session.get = AsyncMock(return_value=target)
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.merge = AsyncMock()
    session.commit = AsyncMock()
    return session


def _make_strategy() -> MagicMock:
    strategy = MagicMock()
    strategy.destroy_user_tokens = AsyncMock()
    return strategy


@pytest.mark.asyncio
async def test_reset_password_success(monkeypatch: pytest.MonkeyPatch) -> None:
    target = _make_target()
    session = _make_session(target)
    strategy = _make_strategy()
    monkeypatch.setattr(users_routes, "write_operation_log", AsyncMock())

    result = await users_routes.reset_user_password(
        user_id=10,
        request=SimpleNamespace(client=SimpleNamespace(host="127.0.0.1")),
        session=session,
        user=_make_actor(),
        strategy=strategy,
    )

    assert "temporaryPassword" in result
    assert result["message"] == "密码重置成功"
    assert target.must_change_password is True
    strategy.destroy_user_tokens.assert_awaited_once_with(10)


@pytest.mark.asyncio
async def test_reset_password_user_not_found() -> None:
    session = _make_session(None)
    strategy = _make_strategy()

    with pytest.raises(HTTPException) as exc:
        await users_routes.reset_user_password(
            user_id=999,
            request=SimpleNamespace(client=SimpleNamespace(host="127.0.0.1")),
            session=session,
            user=_make_actor(),
            strategy=strategy,
        )

    assert exc.value.status_code == 404
