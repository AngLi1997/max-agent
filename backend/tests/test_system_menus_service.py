import pytest

from app.models.menu import Menu
from app.services.system_menus import build_menu_tree, validate_menu_parent


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


def test_validate_menu_parent_rejects_missing_parent() -> None:
    menus_by_id = {1: Menu(id=1, name="系统", path="/setting", status="active", sort=1)}

    with pytest.raises(ValueError, match="父菜单不存在"):
        validate_menu_parent(menu_id=1, parent_id=999, menus_by_id=menus_by_id)


def test_build_menu_tree_nests_flat_menu_list() -> None:
    root_b = Menu(id=2, name="B", path="/b", status="active", sort=2, parent_id=None, permission="", icon="", component="")
    root_a = Menu(id=1, name="A", path="/a", status="active", sort=1, parent_id=None, permission="", icon="", component="")
    child_a2 = Menu(id=4, name="A-2", path="/a/2", status="active", sort=2, parent_id=1, permission="", icon="", component="")
    child_a1 = Menu(id=3, name="A-1", path="/a/1", status="active", sort=1, parent_id=1, permission="", icon="", component="")
    grandchild = Menu(id=5, name="A-1-1", path="/a/1/1", status="active", sort=1, parent_id=3, permission="", icon="", component="")

    tree = build_menu_tree([child_a2, root_b, grandchild, root_a, child_a1])

    assert [item.id for item in tree] == [1, 2]
    assert [item.id for item in tree[0].children] == [3, 4]
    assert [item.id for item in tree[0].children[0].children] == [5]
    assert tree[1].children == []
