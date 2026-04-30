from app.db.seed import ALL_MENUS, PERMISSIONS


def test_seeded_menu_permissions_have_definitions() -> None:
    permission_identifiers = {permission["identifier"] for permission in PERMISSIONS}

    missing_permissions = [
        menu["permission"]
        for menu in ALL_MENUS
        if menu.get("permission") and menu["permission"] not in permission_identifiers
    ]

    assert not missing_permissions, f"Missing permission definitions: {missing_permissions}"


def test_reset_password_permission_is_seeded() -> None:
    permission_identifiers = {p["identifier"] for p in PERMISSIONS}
    assert "user:reset-password" in permission_identifiers
