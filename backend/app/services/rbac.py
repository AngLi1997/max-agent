from collections.abc import Iterable

from app.models.menu import Menu
from app.models.user import User


def collect_user_permissions(user: User) -> set[str]:
    if user.is_superuser:
        return {
            permission.identifier
            for role in user.roles
            for permission in role.permissions
            if permission.status == "active"
        }
    permissions: set[str] = set()
    for role in user.roles:
        if role.status != "active":
            continue
        for permission in role.permissions:
            if permission.status == "active":
                permissions.add(permission.identifier)
    return permissions


def build_visible_menu_tree(menus: Iterable[Menu], permissions: set[str]) -> list[dict]:
    result: list[dict] = []
    for menu in sorted(menus, key=lambda item: item.sort):
        if menu.status != "active":
            continue
        children = build_visible_menu_tree(menu.children, permissions) if menu.children else []
        visible = not menu.permission or menu.permission in permissions or bool(children)
        if not visible:
            continue
        result.append(
            {
                "id": menu.id,
                "name": menu.name,
                "path": menu.path,
                "permission": menu.permission,
                "icon": menu.icon,
                "component": menu.component,
                "sort": menu.sort,
                "status": menu.status,
                "parentId": menu.parent_id,
                "children": children,
            }
        )
    return result
