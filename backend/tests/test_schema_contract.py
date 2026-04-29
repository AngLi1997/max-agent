from app.models import LoginLog, Menu, OperationLog, Role, SystemConfig, User


def test_user_model_has_status_builtin_and_password_reset_flags() -> None:
    columns = User.__table__.c
    assert "status" in columns
    assert "is_builtin" in columns
    assert "must_change_password" in columns


def test_role_model_has_builtin_flag() -> None:
    assert "is_builtin" in Role.__table__.c


def test_menu_model_has_component_column() -> None:
    assert "component" in Menu.__table__.c


def test_new_models_are_exported() -> None:
    assert SystemConfig.__tablename__ == "system_config"
    assert OperationLog.__tablename__ == "operation_log"
    assert LoginLog.__tablename__ == "login_log"
