from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.api.routes import configs as configs_routes
from app.api.routes import permissions as permissions_routes
from app.api.routes import roles as roles_routes
from app.schemas.permission import PermissionCreateRequest
from app.schemas.role import RoleCreateRequest
from app.schemas.system_config import ConfigCreateRequest


class DummySession:
    def __init__(self) -> None:
        self.add = lambda _: None
        self.flush = AsyncMock()
        self.commit = AsyncMock(side_effect=IntegrityError("stmt", "params", Exception("dup")))
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
