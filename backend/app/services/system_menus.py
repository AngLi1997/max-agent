from collections import defaultdict

from app.models.menu import Menu
from app.schemas.menu import MenuTreeItem


def apply_menu_status(menu: Menu, status: str) -> None:
    menu.status = status


def validate_menu_parent(*, menu_id: int | None, parent_id: int | None, menus_by_id: dict[int, Menu]) -> None:
    if parent_id is None:
        return
    if parent_id not in menus_by_id:
        raise ValueError("父菜单不存在")
    if menu_id is not None and menu_id == parent_id:
        raise ValueError("菜单不能将自己设为父菜单")

    if menu_id is None:
        return

    current_id = parent_id
    visited: set[int] = set()
    while current_id is not None:
        if current_id in visited:
            break
        if current_id == menu_id:
            raise ValueError("菜单层级不能形成循环")
        visited.add(current_id)
        parent = menus_by_id.get(current_id)
        if parent is None:
            break
        current_id = parent.parent_id


def build_menu_tree(menus: list[Menu]) -> list[MenuTreeItem]:
    grouped: dict[int | None, list[Menu]] = defaultdict(list)
    for menu in menus:
        grouped[menu.parent_id].append(menu)

    for siblings in grouped.values():
        siblings.sort(key=lambda item: item.sort)

    def to_tree_item(menu: Menu) -> MenuTreeItem:
        return MenuTreeItem(
            id=menu.id,
            name=menu.name,
            path=menu.path,
            permission=menu.permission,
            icon=menu.icon,
            component=menu.component,
            sort=menu.sort,
            status=menu.status,
            parentId=menu.parent_id,
            children=[to_tree_item(child) for child in grouped.get(menu.id, [])],
        )

    return [to_tree_item(root) for root in grouped.get(None, [])]
