import pytest

from app.models.menu import Menu
from app.services.system_menus import validate_menu_parent


def test_validate_menu_parent_rejects_self_parent() -> None:
    menus_by_id = {1: Menu(id=1, name="系统", path="/setting", status="active", sort=1)}
    with pytest.raises(ValueError, match="不能将自己设为父菜单"):
        validate_menu_parent(menu_id=1, parent_id=1, menus_by_id=menus_by_id)


def test_validate_menu_parent_rejects_cycle() -> None:
    root = Menu(id=1, name="root", path="/root", status="active", sort=1, parent_id=None)
    child = Menu(id=2, name="child", path="/child", status="active", sort=1, parent_id=1)
    grandchild = Menu(id=3, name="leaf", path="/leaf", status="active", sort=1, parent_id=2)
    menus_by_id = {1: root, 2: child, 3: grandchild}

    with pytest.raises(ValueError, match="不能形成循环"):
        validate_menu_parent(menu_id=1, parent_id=3, menus_by_id=menus_by_id)
