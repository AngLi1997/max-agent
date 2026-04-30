from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db_session
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.schemas.common import ListResponse
from app.schemas.role import (
    RoleCreateRequest,
    RoleListItem,
    RolePermissionAssignRequest,
    RoleUpdateRequest,
    StatusUpdateRequest,
)
from app.services.audit import write_operation_log
from app.services.auth import current_active_user
from app.services.authorization import require_permission
from app.services.system_roles import (
    delete_role_or_raise,
    replace_role_permissions,
    validate_permission_ids,
)
from app.utils.request import get_client_ip
from app.utils.time import format_datetime

router = APIRouter(prefix="/roles", tags=["roles"])


def _role_integrity_error_message(error: IntegrityError) -> str:
    detail = str(error.orig)
    if "role.name" in detail or "name" in detail:
        return "角色名称已存在"
    if "role.code" in detail or "code" in detail:
        return "角色编码已存在"
    return "角色数据违反唯一约束"


@router.get("/", response_model=ListResponse[RoleListItem])
async def list_roles(
    name: str | None = None,
    status: str | None = None,
    session: AsyncSession = Depends(get_db_session),
    _user: User = Depends(require_permission("setting:role")),
) -> ListResponse[RoleListItem]:
    q = select(Role)
    if name:
        q = q.where(Role.name.ilike(f"%{name}%"))
    if status:
        q = q.where(Role.status == status)
    rows = (await session.scalars(q)).all()
    total = len(rows)
    items = [
        RoleListItem(
            id=r.id,
            name=r.name,
            code=r.code,
            description=r.description,
            status=r.status,
            isBuiltin=r.is_builtin,
            createdAt=format_datetime(r.created_at),
        )
        for r in rows
    ]
    return ListResponse(list=items, total=total)


@router.post("/", response_model=RoleListItem)
async def create_role(
    payload: RoleCreateRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(require_permission("role:create")),
) -> RoleListItem:
    role = Role(
        name=payload.name,
        code=payload.code,
        description=payload.description,
        status=payload.status,
    )
    session.add(role)
    try:
        await session.flush()
        await write_operation_log(
            session,
            operator_id=user.id,
            operator_name=user.username,
            module="角色管理",
            action="创建角色",
            method="POST",
            result="成功",
            detail=f"创建角色 {role.name}",
            ip=get_client_ip(request),
        )
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_role_integrity_error_message(exc))
    await session.refresh(role)
    return RoleListItem(
        id=role.id,
        name=role.name,
        code=role.code,
        description=role.description,
        status=role.status,
        isBuiltin=role.is_builtin,
        createdAt=format_datetime(role.created_at),
    )


@router.put("/{role_id}", response_model=RoleListItem)
async def update_role(
    role_id: int,
    payload: RoleUpdateRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(require_permission("role:update")),
) -> RoleListItem:
    role = await session.get(Role, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    role.name = payload.name
    role.code = payload.code
    role.description = payload.description
    role.status = payload.status
    session.add(role)
    try:
        await write_operation_log(
            session,
            operator_id=user.id,
            operator_name=user.username,
            module="角色管理",
            action="更新角色",
            method="PUT",
            result="成功",
            detail=f"更新角色 {role.name}",
            ip=get_client_ip(request),
        )
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_role_integrity_error_message(exc))
    await session.refresh(role)
    return RoleListItem(
        id=role.id,
        name=role.name,
        code=role.code,
        description=role.description,
        status=role.status,
        isBuiltin=role.is_builtin,
        createdAt=format_datetime(role.created_at),
    )


@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(require_permission("role:delete")),
) -> dict[str, str]:
    role = await session.get(Role, role_id, options=[selectinload(Role.users)])
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    linked_user_count = len(role.users)
    try:
        delete_role_or_raise(role, linked_user_count=linked_user_count)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await session.delete(role)
    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="角色管理",
        action="删除角色",
        method="DELETE",
        result="成功",
        detail=f"删除角色 {role.name}",
        ip=get_client_ip(request),
    )
    await session.commit()
    return {"message": "删除成功"}


@router.patch("/{role_id}/status")
async def update_role_status(
    role_id: int,
    payload: StatusUpdateRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(require_permission("role:status")),
) -> dict[str, str]:
    role = await session.get(Role, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    role.status = payload.status
    session.add(role)
    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="角色管理",
        action="更新角色状态",
        method="PATCH",
        result="成功",
        detail=f"角色 {role.name} 状态更新为 {payload.status}",
        ip=get_client_ip(request),
    )
    await session.commit()
    return {"message": "状态更新成功"}


@router.get("/{role_id}/permissions")
async def get_role_permissions(
    role_id: int,
    session: AsyncSession = Depends(get_db_session),
    _user: User = Depends(require_permission("setting:role")),
) -> dict[str, list[int]]:
    role = await session.get(Role, role_id, options=[selectinload(Role.permissions)])
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    return {"permissionIds": [p.id for p in role.permissions]}


@router.put("/{role_id}/permissions")
async def assign_role_permissions(
    role_id: int,
    payload: RolePermissionAssignRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(require_permission("role:assign-permission")),
) -> dict[str, str]:
    role = await session.get(Role, role_id, options=[selectinload(Role.permissions)])
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    permissions = (
        await session.scalars(
            select(Permission).where(Permission.id.in_(payload.permissionIds))
        )
    ).all()
    try:
        validate_permission_ids(payload.permissionIds, list(permissions))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    replace_role_permissions(role, list(permissions))
    session.add(role)
    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="角色管理",
        action="分配权限",
        method="PUT",
        result="成功",
        detail=f"角色 {role.name} 分配了 {len(permissions)} 个权限",
        ip=get_client_ip(request),
    )
    await session.commit()
    return {"message": "权限分配成功"}
