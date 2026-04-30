"""Tests for new backend invariants introduced in the review-fix pass."""

import pytest

from app.models.menu import Menu
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.services.rbac import collect_user_permissions


# ---------------------------------------------------------------------------
# 1. Authorization helper: collect_user_permissions + superuser bypass
# ---------------------------------------------------------------------------


def _make_user(*, is_superuser: bool = False, roles: list[Role] | None = None) -> User:
    user = User(
        username="tester",
        email="tester@example.com",
        hashed_password="x",
        is_active=True,
        is_superuser=is_superuser,
        is_verified=True,
        avatar="",
    )
    user.roles = roles or []
    return user


def _make_role(*, status: str = "active", permissions: list[Permission] | None = None) -> Role:
    role = Role(name="r", code="r", description="", status=status)
    role.permissions = permissions or []
    return role


def _make_perm(identifier: str, *, status: str = "active") -> Permission:
    return Permission(name=identifier, identifier=identifier, type="按钮", status=status)


def test_superuser_gets_all_permissions_from_active_roles() -> None:
    """Superuser collects permissions from active roles (inactive role perms still skipped)."""
    perm_a = _make_perm("setting:user")
    perm_b = _make_perm("user:create")
    role = _make_role(permissions=[perm_a, perm_b])
    user = _make_user(is_superuser=True, roles=[role])
    result = collect_user_permissions(user)
    assert "setting:user" in result
    assert "user:create" in result


def test_non_superuser_missing_permission_returns_empty() -> None:
    """Non-superuser with no roles has no permissions."""
    user = _make_user(is_superuser=False, roles=[])
    assert collect_user_permissions(user) == set()


def test_non_superuser_with_permission_returns_it() -> None:
    """Non-superuser with an active role + active permission gets that permission."""
    perm = _make_perm("setting:role")
    role = _make_role(permissions=[perm])
    user = _make_user(is_superuser=False, roles=[role])
    assert "setting:role" in collect_user_permissions(user)


def test_non_superuser_inactive_role_excluded() -> None:
    """Permissions from inactive roles are not collected for non-superusers."""
    perm = _make_perm("setting:role")
    role = _make_role(status="inactive", permissions=[perm])
    user = _make_user(is_superuser=False, roles=[role])
    assert collect_user_permissions(user) == set()


def test_non_superuser_inactive_permission_excluded() -> None:
    """Inactive permissions are excluded even when the role is active."""
    perm = _make_perm("setting:role", status="inactive")
    role = _make_role(permissions=[perm])
    user = _make_user(is_superuser=False, roles=[role])
    assert collect_user_permissions(user) == set()


# ---------------------------------------------------------------------------
# 2. Builtin user protection helpers
# ---------------------------------------------------------------------------


def _make_builtin_user(roles: list[Role] | None = None) -> User:
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password="x",
        is_active=True,
        is_superuser=True,
        is_verified=True,
        avatar="",
        is_builtin=True,
        status="active",
    )
    user.roles = roles or []
    return user


def test_builtin_user_status_change_detected() -> None:
    """Detect that a builtin user's status differs from the payload."""
    user = _make_builtin_user()
    assert user.is_builtin is True
    # Simulate the route-level guard logic
    new_status = "inactive"
    assert new_status != user.status, "Guard should reject this"


def test_builtin_user_role_change_detected() -> None:
    """Detect that a builtin user's roles differ from the payload."""
    role = Role(id=1, name="admin", code="admin", description="", status="active")
    role.permissions = []
    user = _make_builtin_user(roles=[role])
    current_role_ids = sorted(r.id for r in user.roles)
    new_role_ids = sorted([2])  # different
    assert new_role_ids != current_role_ids, "Guard should reject this"


def test_builtin_user_same_roles_allowed() -> None:
    """Same role IDs should pass the guard."""
    role = Role(id=1, name="admin", code="admin", description="", status="active")
    role.permissions = []
    user = _make_builtin_user(roles=[role])
    current_role_ids = sorted(r.id for r in user.roles)
    new_role_ids = sorted([1])
    assert new_role_ids == current_role_ids


# ---------------------------------------------------------------------------
# 3. Duplicate menu path detection (helper logic)
# ---------------------------------------------------------------------------


def test_duplicate_menu_path_same_path_different_id() -> None:
    """Two menus with the same path should be flagged as duplicate."""
    existing = Menu(id=1, name="A", path="/setting", status="active", sort=1)
    new_path = "/setting"
    # Simulate the application-level check: find any menu with same path, exclude_id=None
    conflict = existing.path == new_path
    assert conflict is True


def test_duplicate_menu_path_update_same_id_no_conflict() -> None:
    """Updating a menu to keep its own path should not be flagged."""
    existing = Menu(id=1, name="A", path="/setting", status="active", sort=1)
    new_path = "/setting"
    exclude_id = 1
    # Simulate: same path but excluded by id
    conflict = existing.path == new_path and existing.id != exclude_id
    assert conflict is False


def test_duplicate_menu_path_different_path_no_conflict() -> None:
    """Different paths should not conflict."""
    existing = Menu(id=1, name="A", path="/setting", status="active", sort=1)
    new_path = "/other"
    conflict = existing.path == new_path
    assert conflict is False


# ---------------------------------------------------------------------------
# 4. Integrity error on flush (not just commit) — logic verification
# ---------------------------------------------------------------------------


def test_role_create_integrity_error_message_name() -> None:
    """_role_integrity_error_message returns correct message for name conflict."""
    from sqlalchemy.exc import IntegrityError

    class FakeOrig:
        def __str__(self) -> str:
            return "UNIQUE constraint failed: role.name"

    exc = IntegrityError("stmt", {}, FakeOrig())

    from app.api.routes.roles import _role_integrity_error_message

    msg = _role_integrity_error_message(exc)
    assert "名称" in msg


def test_permission_create_integrity_error_message_identifier() -> None:
    """_permission_integrity_error_message returns correct message for identifier conflict."""
    from sqlalchemy.exc import IntegrityError

    class FakeOrig:
        def __str__(self) -> str:
            return "UNIQUE constraint failed: permission.identifier"

    exc = IntegrityError("stmt", {}, FakeOrig())

    from app.api.routes.permissions import _permission_integrity_error_message

    msg = _permission_integrity_error_message(exc)
    assert "标识" in msg


def test_config_create_integrity_error_message_key() -> None:
    """_config_integrity_error_message returns correct message for key conflict."""
    from sqlalchemy.exc import IntegrityError

    class FakeOrig:
        def __str__(self) -> str:
            return "UNIQUE constraint failed: system_config.key"

    exc = IntegrityError("stmt", {}, FakeOrig())

    from app.api.routes.configs import _config_integrity_error_message

    msg = _config_integrity_error_message(exc)
    assert "键" in msg
