from app.models.permission import Permission
from app.models.role import Role


def delete_role_or_raise(role: Role, *, linked_user_count: int) -> None:
    if role.is_builtin:
        raise ValueError("内置角色不允许删除")
    if linked_user_count > 0:
        raise ValueError("角色仍被用户绑定，不能删除")


def replace_role_permissions(role: Role, permissions: list[Permission]) -> None:
    role.permissions = list(permissions)
