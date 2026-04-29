"""Reusable RBAC permission enforcement for FastAPI routes."""

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db_session
from app.models.role import Role
from app.models.user import User
from app.services.auth import current_active_user
from app.services.rbac import collect_user_permissions


def require_permission(permission: str) -> Callable:
    """Return a FastAPI dependency that enforces the given permission.

    Superusers bypass the check.  Non-superusers must have *permission* in
    their aggregated active-role permissions; otherwise HTTP 403 is raised.
    """

    async def _check(
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_db_session),
    ) -> User:
        if user.is_superuser:
            return user

        # Load roles + permissions for the current user
        full_user = await session.scalar(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(User.id == user.id)
        )
        if full_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

        user_permissions = collect_user_permissions(full_user)
        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要权限: {permission}",
            )
        return full_user

    return _check
