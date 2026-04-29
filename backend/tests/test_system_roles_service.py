import pytest

from app.models.permission import Permission
from app.models.role import Role
from app.services.system_roles import delete_role_or_raise, replace_role_permissions


def test_delete_role_blocks_builtin_role() -> None:
    role = Role(name="超级管理员", code="admin", description="", status="active", is_builtin=True)
    with pytest.raises(ValueError, match="内置角色不允许删除"):
        delete_role_or_raise(role, linked_user_count=0)


def test_replace_role_permissions_overwrites_existing_list() -> None:
    role = Role(name="编辑", code="editor", description="", status="active")
    old = Permission(name="旧权限", identifier="old", type="按钮", status="active")
    new = Permission(name="新权限", identifier="new", type="按钮", status="active")
    role.permissions = [old]
    replace_role_permissions(role, [new])
    assert [p.identifier for p in role.permissions] == ["new"]
