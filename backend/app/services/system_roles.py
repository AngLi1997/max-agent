from app.models.permission import Permission
from app.models.role import Role


def validate_permission_ids(requested_ids: list[int], permissions: list[Permission]) -> None:
    if len(requested_ids) != len(set(requested_ids)):
        raise ValueError("permissionIds 包含重复项")

    existing_ids = {permission.id for permission in permissions}
    missing_ids = sorted({permission_id for permission_id in requested_ids if permission_id not in existing_ids})
    if missing_ids:
        raise ValueError(f"权限不存在: {', '.join(str(i) for i in missing_ids)}")


def delete_role_or_raise(role: Role, *, linked_user_count: int) -> None:
    if role.is_builtin:
        raise ValueError("内置角色不允许删除")
    if linked_user_count > 0:
        raise ValueError("角色仍被用户绑定，不能删除")


def replace_role_permissions(role: Role, permissions: list[Permission]) -> None:
    role.permissions = list(permissions)
