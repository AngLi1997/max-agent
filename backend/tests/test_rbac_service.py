from app.models.menu import Menu
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.services.rbac import build_visible_menu_tree, collect_user_permissions


def test_collect_user_permissions_skips_inactive_roles_and_permissions() -> None:
    read = Permission(name="用户查看", identifier="setting:user", type="菜单", status="active")
    hidden = Permission(name="已禁用权限", identifier="setting:hidden", type="按钮", status="inactive")
    active_role = Role(name="编辑", code="editor", description="", status="active")
    inactive_role = Role(name="访客", code="viewer", description="", status="inactive")
    active_role.permissions = [read, hidden]
    inactive_role.permissions = [Permission(name="ignored", identifier="ignored", type="按钮", status="active")]
    user = User(username="editor", email="editor@example.com", hashed_password="x", is_active=True, is_superuser=False, is_verified=True, avatar="")
    user.roles = [active_role, inactive_role]

    assert collect_user_permissions(user) == {"setting:user"}


def test_build_visible_menu_tree_keeps_visible_parent() -> None:
    parent = Menu(name="系统设置", path="/setting", permission="setting:view", icon="SettingOutlined", component="Layout", sort=1, status="active", parent_id=None)
    child = Menu(name="用户管理", path="/setting/user", permission="setting:user", icon="UserOutlined", component="SettingUser", sort=1, status="active", parent_id=1)
    parent.children = [child]

    result = build_visible_menu_tree([parent], {"setting:user"})
    assert result[0]["path"] == "/setting"
    assert result[0]["children"][0]["path"] == "/setting/user"
