import pytest
from pydantic import ValidationError

from app.models import LoginLog, Menu, OperationLog, Role, SystemConfig, User
from app.schemas.user import UserCreateRequest, UserUpdateRequest


def test_user_model_has_status_builtin_and_password_reset_flags() -> None:
    columns = User.__table__.c
    assert "status" in columns
    assert "is_builtin" in columns
    assert "must_change_password" in columns

    assert columns.status.nullable is False
    assert columns.is_builtin.nullable is False
    assert columns.must_change_password.nullable is False


def test_role_model_has_builtin_flag() -> None:
    columns = Role.__table__.c
    assert "is_builtin" in columns
    assert columns.is_builtin.nullable is False


def test_menu_model_has_component_column() -> None:
    columns = Menu.__table__.c
    assert "component" in columns
    assert columns.component.nullable is False


def test_new_models_are_exported() -> None:
    assert SystemConfig.__tablename__ == "system_config"
    assert OperationLog.__tablename__ == "operation_log"
    assert LoginLog.__tablename__ == "login_log"


def test_system_config_key_is_unique_and_indexed() -> None:
    key_column = SystemConfig.__table__.c.key
    assert key_column.nullable is False
    assert key_column.unique is True
    assert key_column.index is True


def test_operation_log_operator_id_is_indexed() -> None:
    operator_id_column = OperationLog.__table__.c.operator_id
    assert operator_id_column.index is True


def test_login_log_user_id_is_indexed() -> None:
    user_id_column = LoginLog.__table__.c.user_id
    assert user_id_column.index is True


def test_new_required_columns_remain_non_nullable() -> None:
    system_config_columns = SystemConfig.__table__.c
    operation_log_columns = OperationLog.__table__.c
    login_log_columns = LoginLog.__table__.c

    assert system_config_columns.name.nullable is False
    assert system_config_columns.key.nullable is False
    assert system_config_columns.value.nullable is False

    assert operation_log_columns.module.nullable is False
    assert operation_log_columns.action.nullable is False
    assert operation_log_columns.method.nullable is False
    assert operation_log_columns.result.nullable is False

    assert login_log_columns.result.nullable is False


def test_user_schema_status_only_accepts_active_or_inactive() -> None:
    with pytest.raises(ValidationError):
        UserCreateRequest(username="u1", email="u1@example.com", roleIds=[1], status="disabled")

    with pytest.raises(ValidationError):
        UserUpdateRequest(username="u2", email="u2@example.com", roleIds=[1], status="disabled")
