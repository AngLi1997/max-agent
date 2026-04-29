from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.permission import Permission
from app.models.user import User
from app.schemas.common import ListResponse
from app.schemas.permission import (
    PermissionCreateRequest,
    PermissionListItem,
    PermissionUpdateRequest,
)
from app.schemas.role import StatusUpdateRequest
from app.services.audit import write_operation_log
from app.services.auth import current_active_user
from app.services.system_permissions import delete_permission_or_raise

router = APIRouter(prefix="/permissions", tags=["permissions"])


def _permission_integrity_error_message(error: IntegrityError) -> str:
    detail = str(error.orig)
    if "permission.identifier" in detail or "identifier" in detail:
        return "权限标识已存在"
    return "权限数据违反唯一约束"


@router.get("/", response_model=ListResponse[PermissionListItem])
async def list_permissions(
    name: str | None = None,
    type: str | None = None,
    session: AsyncSession = Depends(get_db_session),
    _user: User = Depends(current_active_user),
) -> ListResponse[PermissionListItem]:
    q = select(Permission)
    if name:
        q = q.where(Permission.name.ilike(f"%{name}%"))
    if type:
        q = q.where(Permission.type == type)
    rows = (await session.scalars(q)).all()
    items = [
        PermissionListItem(
            id=p.id,
            name=p.name,
            identifier=p.identifier,
            type=p.type,
            status=p.status,
            createdAt=p.created_at.isoformat(sep=" ", timespec="seconds"),
        )
        for p in rows
    ]
    return ListResponse(list=items, total=len(items))


@router.post("/", response_model=PermissionListItem)
async def create_permission(
    payload: PermissionCreateRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
) -> PermissionListItem:
    perm = Permission(
        name=payload.name,
        identifier=payload.identifier,
        type=payload.type,
        status=payload.status,
    )
    session.add(perm)
    await session.flush()
    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="权限管理",
        action="创建权限",
        method="POST",
        result="成功",
        detail=f"创建权限 {perm.name}",
        ip=request.client.host if request.client else "",
    )
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_permission_integrity_error_message(exc))
    await session.refresh(perm)
    return PermissionListItem(
        id=perm.id,
        name=perm.name,
        identifier=perm.identifier,
        type=perm.type,
        status=perm.status,
        createdAt=perm.created_at.isoformat(sep=" ", timespec="seconds"),
    )


@router.put("/{perm_id}", response_model=PermissionListItem)
async def update_permission(
    perm_id: int,
    payload: PermissionUpdateRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
) -> PermissionListItem:
    perm = await session.get(Permission, perm_id)
    if perm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="权限不存在")
    perm.name = payload.name
    perm.identifier = payload.identifier
    perm.type = payload.type
    perm.status = payload.status
    session.add(perm)
    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="权限管理",
        action="更新权限",
        method="PUT",
        result="成功",
        detail=f"更新权限 {perm.name}",
        ip=request.client.host if request.client else "",
    )
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_permission_integrity_error_message(exc))
    await session.refresh(perm)
    return PermissionListItem(
        id=perm.id,
        name=perm.name,
        identifier=perm.identifier,
        type=perm.type,
        status=perm.status,
        createdAt=perm.created_at.isoformat(sep=" ", timespec="seconds"),
    )


@router.delete("/{perm_id}")
async def delete_permission(
    perm_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
) -> dict[str, str]:
    perm = await session.get(Permission, perm_id)
    if perm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="权限不存在")
    linked_role_count_result = await session.execute(
        select(Permission)
        .where(Permission.id == perm_id)
        .join(Permission.roles)
    )
    linked_role_count = len(linked_role_count_result.scalars().all())
    try:
        delete_permission_or_raise(linked_role_count=linked_role_count)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await session.delete(perm)
    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="权限管理",
        action="删除权限",
        method="DELETE",
        result="成功",
        detail=f"删除权限 {perm.name}",
        ip=request.client.host if request.client else "",
    )
    await session.commit()
    return {"message": "删除成功"}


@router.patch("/{perm_id}/status")
async def update_permission_status(
    perm_id: int,
    payload: StatusUpdateRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
) -> dict[str, str]:
    perm = await session.get(Permission, perm_id)
    if perm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="权限不存在")
    perm.status = payload.status
    session.add(perm)
    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="权限管理",
        action="更新权限状态",
        method="PATCH",
        result="成功",
        detail=f"权限 {perm.name} 状态更新为 {payload.status}",
        ip=request.client.host if request.client else "",
    )
    await session.commit()
    return {"message": "状态更新成功"}
