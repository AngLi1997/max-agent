import pytest
from pwdlib import PasswordHash

from app.models.user import User
from app.services.system_users import (
    build_current_user_payload,
    change_own_password,
    create_temporary_password,
    delete_user_or_raise,
)


password_hash = PasswordHash.recommended()


def test_build_current_user_payload_includes_roles_permissions_menus() -> None:
    user = User(username="admin", email="admin@example.com", hashed_password="x", is_active=True, is_superuser=True, is_verified=True, avatar="")
    payload = build_current_user_payload(
        user=user,
        roles=[{"id": 1, "name": "超级管理员", "code": "admin"}],
        permissions={"setting:user"},
        menus=[{"path": "/setting/user"}],
    )
    assert payload["roles"][0]["code"] == "admin"
    assert payload["permissions"] == ["setting:user"]
    assert payload["menus"][0]["path"] == "/setting/user"


def test_change_own_password_clears_force_change_flag() -> None:
    user = User(
        username="editor",
        email="editor@example.com",
        hashed_password=password_hash.hash("old-pass"),
        is_active=True,
        is_superuser=False,
        is_verified=True,
        avatar="",
        must_change_password=True,
    )

    change_own_password(user, old_password="old-pass", new_password="new-pass")
    assert user.must_change_password is False


def test_create_temporary_password_returns_non_empty_secret() -> None:
    password = create_temporary_password()
    assert len(password) >= 12


def test_delete_user_blocks_builtin_user() -> None:
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password="x",
        is_active=True,
        is_superuser=True,
        is_verified=True,
        avatar="",
        is_builtin=True,
    )
    with pytest.raises(ValueError, match="内置用户不允许删除"):
        delete_user_or_raise(user)


def test_reset_password_for_user_sets_new_hash_and_force_change() -> None:
    from app.services.system_users import reset_password_for_user

    user = User(
        username="editor",
        email="editor@example.com",
        hashed_password=password_hash.hash("old-pass"),
        is_active=True,
        is_superuser=False,
        is_verified=True,
        avatar="",
        must_change_password=False,
    )
    old_hash = user.hashed_password
    temp_password = reset_password_for_user(user)

    assert len(temp_password) >= 12
    assert user.hashed_password != old_hash
    assert user.must_change_password is True
    assert password_hash.verify(temp_password, user.hashed_password)
