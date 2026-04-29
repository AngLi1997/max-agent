from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.api.routes import configs as configs_routes
from app.api.routes import permissions as permissions_routes
from app.api.routes import roles as roles_routes
from app.api.routes import users as users_routes
from app.models.role import Role
from app.models.user import User
from app.schemas.permission import PermissionCreateRequest
from app.schemas.role import RoleCreateRequest
from app.schemas.system_config import ConfigCreateRequest
from app.schemas.user import UserUpdateRequest


class DummySession:
    def __init__(self) -> None:
        self.add = lambda _: None
        self.flush = AsyncMock()
        self.commit = AsyncMock(side_effect=IntegrityError("stmt", "params", Exception("dup")))
        self.rollback = AsyncMock()
        self.refresh = AsyncMock()


class DummyScalarResult:
    def __init__(self, values: list[Role]) -> None:
        self._values = values

    def all(self) -> list[Role]:
        return self._values


class DummyUserUpdateSession:
    def __init__(self, *, target: User, roles: list[Role]) -> None:
        self.add = lambda _: None
        self.get = AsyncMock(return_value=target)
        self.scalars = AsyncMock(return_value=DummyScalarResult(roles))
        self.flush = AsyncMock()
        self.commit = AsyncMock()
        self.rollback = AsyncMock()
        self.refresh = AsyncMock()


@pytest.mark.asyncio
async def test_create_role_maps_integrity_error_to_http_409_and_rolls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    session = DummySession()
    monkeypatch.setattr(roles_routes, "write_operation_log", AsyncMock())

    with pytest.raises(HTTPException) as exc:
        await roles_routes.create_role(
            payload=RoleCreateRequest(name="admin", code="admin", description="", status="active"),
            request=SimpleNamespace(client=SimpleNamespace(host="127.0.0.1")),
            session=session,
            user=SimpleNamespace(id=1, username="tester"),
        )

    assert exc.value.status_code == 409
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_permission_maps_integrity_error_to_http_409_and_rolls_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = DummySession()
    monkeypatch.setattr(permissions_routes, "write_operation_log", AsyncMock())

    with pytest.raises(HTTPException) as exc:
        await permissions_routes.create_permission(
            payload=PermissionCreateRequest(
                name="查看用户",
                identifier="user:view",
                type="menu",
                status="active",
            ),
            request=SimpleNamespace(client=SimpleNamespace(host="127.0.0.1")),
            session=session,
            user=SimpleNamespace(id=1, username="tester"),
        )

    assert exc.value.status_code == 409
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_config_maps_integrity_error_to_http_409_and_rolls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    session = DummySession()
    monkeypatch.setattr(configs_routes, "write_operation_log", AsyncMock())

    with pytest.raises(HTTPException) as exc:
        await configs_routes.create_config(
            payload=ConfigCreateRequest(name="站点名称", key="site.name", value="Max Agent", description=""),
            request=SimpleNamespace(client=SimpleNamespace(host="127.0.0.1")),
            session=session,
            user=SimpleNamespace(id=1, username="tester"),
        )

    assert exc.value.status_code == 409
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_user_maps_integrity_error_during_log_flush_to_http_409_and_rolls_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = User(
        id=10,
        username="editor",
        email="editor@example.com",
        hashed_password="x",
        is_active=True,
        is_superuser=False,
        is_verified=True,
        avatar="",
        status="active",
    )
    active_role = Role(id=1, name="编辑", code="editor", status="active")
    session = DummyUserUpdateSession(target=target, roles=[active_role])
    monkeypatch.setattr(
        users_routes,
        "write_operation_log",
        AsyncMock(side_effect=IntegrityError("stmt", "params", Exception("dup"))),
    )

    with pytest.raises(HTTPException) as exc:
        await users_routes.update_user(
            user_id=10,
            payload=UserUpdateRequest(
                username="editor2",
                email="editor2@example.com",
                roleIds=[1],
                status="active",
            ),
            request=SimpleNamespace(client=SimpleNamespace(host="127.0.0.1")),
            session=session,
            user=SimpleNamespace(id=1, username="tester"),
        )

    assert exc.value.status_code == 409
    session.rollback.assert_awaited_once()
    session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_update_user_maps_integrity_error_during_flush_to_http_409_and_rolls_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = User(
        id=10,
        username="editor",
        email="editor@example.com",
        hashed_password="x",
        is_active=True,
        is_superuser=False,
        is_verified=True,
        avatar="",
        status="active",
    )
    active_role = Role(id=1, name="编辑", code="editor", status="active")
    session = DummyUserUpdateSession(target=target, roles=[active_role])
    session.flush = AsyncMock(side_effect=IntegrityError("stmt", "params", Exception("dup")))
    monkeypatch.setattr(users_routes, "write_operation_log", AsyncMock())

    with pytest.raises(HTTPException) as exc:
        await users_routes.update_user(
            user_id=10,
            payload=UserUpdateRequest(
                username="editor2",
                email="editor2@example.com",
                roleIds=[1],
                status="active",
            ),
            request=SimpleNamespace(client=SimpleNamespace(host="127.0.0.1")),
            session=session,
            user=SimpleNamespace(id=1, username="tester"),
        )

    assert exc.value.status_code == 409
    session.rollback.assert_awaited_once()
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_user_rejects_empty_role_ids_with_http_400() -> None:
    target = User(
        id=10,
        username="editor",
        email="editor@example.com",
        hashed_password="x",
        is_active=True,
        is_superuser=False,
        is_verified=True,
        avatar="",
        status="active",
    )
    session = DummyUserUpdateSession(target=target, roles=[])

    with pytest.raises(HTTPException) as exc:
        await users_routes.update_user(
            user_id=10,
            payload=UserUpdateRequest(
                username="editor2",
                email="editor2@example.com",
                roleIds=[],
                status="active",
            ),
            request=SimpleNamespace(client=SimpleNamespace(host="127.0.0.1")),
            session=session,
            user=SimpleNamespace(id=1, username="tester"),
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "角色列表不能为空"


@pytest.mark.asyncio
async def test_update_user_rejects_inactive_role_with_http_400() -> None:
    target = User(
        id=10,
        username="editor",
        email="editor@example.com",
        hashed_password="x",
        is_active=True,
        is_superuser=False,
        is_verified=True,
        avatar="",
        status="active",
    )
    inactive_role = Role(id=2, name="访客", code="visitor", status="inactive")
    session = DummyUserUpdateSession(target=target, roles=[inactive_role])

    with pytest.raises(HTTPException) as exc:
        await users_routes.update_user(
            user_id=10,
            payload=UserUpdateRequest(
                username="editor2",
                email="editor2@example.com",
                roleIds=[2],
                status="active",
            ),
            request=SimpleNamespace(client=SimpleNamespace(host="127.0.0.1")),
            session=session,
            user=SimpleNamespace(id=1, username="tester"),
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "角色包含已禁用项"
