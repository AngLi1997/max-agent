def delete_permission_or_raise(*, linked_role_count: int) -> None:
    if linked_role_count > 0:
        raise ValueError("权限仍被角色引用，不能删除")
