from app.models.menu import Menu


def apply_menu_status(menu: Menu, status: str) -> None:
    menu.status = status
