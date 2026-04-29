from fastapi import APIRouter, Depends, HTTPException, Request, status
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db_session
from app.models.role import Role
from app.models.user import User
from app.schemas.common import ListResponse
from app.schemas.role import StatusUpdateRequest
from app.schemas.user import CreateUserResponse, RoleSummary, UserCreateRequest, UserListItem, UserUpdateRequest
from app.services.audit import write_operation_log
from app.services.auth import current_active_user
from app.services.system_users import create_temporary_password, delete_user_or_raise

router = APIRouter(prefix="/users", tags=["users"])
password_hash = PasswordHash.recommended()


def _user_integrity_error_message(error: IntegrityError) -> str:
    detail = str(error.orig)
    if "user.username" in detail or "username" in detail:
        return "用户名已存在"
    if "user.email" in detail or "email" in detail:
        return "邮箱已存在"
    return "用户数据违反唯一约束"


def _build_user_item(user: User) -> UserListItem:
    role_items = [RoleSummary(id=r.id, name=r.name, code=r.code) for r in user.roles]
    return UserListItem(
        id=user.id,
        username=user.username,
        email=user.email,
        roles=role_items,
        roleIds=[r.id for r in user.roles],
        status=user.status,
        createdAt=user.created_at.isoformat(sep=" ", timespec="seconds"),
        isBuiltin=user.is_builtin,
    )


async def _load_roles_or_400(session: AsyncSession, role_ids: list[int]) -> list[Role]:
    if not role_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="角色列表不能为空")
    if len(set(role_ids)) != len(role_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="角色ID不允许重复")
    roles = (await session.scalars(select(Role).where(Role.id.in_(role_ids)))).all()
    if len(roles) != len(role_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="存在无效的角色ID")
    inactive_roles = [role.name for role in roles if role.status != "active"]
    if inactive_roles:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="角色包含已禁用项")
    return list(roles)


@router.get("/", response_model=ListResponse[UserListItem])
async def list_users(
    username: str | None = None,
    status: str | None = None,
    session: AsyncSession = Depends(get_db_session),
    _user: User = Depends(current_active_user),
) -> ListResponse[UserListItem]:
    q = select(User).options(selectinload(User.roles))
    if username:
        q = q.where(User.username.ilike(f"%{username}%"))
    if status:
        q = q.where(User.status == status)
    rows = (await session.scalars(q)).all()
    items = [_build_user_item(u) for u in rows]
    return ListResponse(list=items, total=len(items))


@router.post("/", response_model=CreateUserResponse)
async def create_user(
    payload: UserCreateRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
) -> CreateUserResponse:
    roles = await _load_roles_or_400(session, payload.roleIds)
    temporary_password = create_temporary_password()
    new_user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=password_hash.hash(temporary_password),
        is_active=payload.status == "active",
        is_superuser=False,
        is_verified=True,
        avatar="",
        status=payload.status,
        is_builtin=False,
        must_change_password=True,
    )
    new_user.roles = roles
    session.add(new_user)
    try:
        await session.flush()
        await write_operation_log(
            session,
            operator_id=user.id,
            operator_name=user.username,
            module="用户管理",
            action="创建用户",
            method="POST",
            result="成功",
            detail=f"创建用户 {new_user.username}",
            ip=request.client.host if request.client else "",
        )
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_user_integrity_error_message(exc))
    await session.refresh(new_user)
    await session.refresh(new_user, attribute_names=["roles"])
    return CreateUserResponse(user=_build_user_item(new_user), temporaryPassword=temporary_password)


@router.put("/{user_id}", response_model=UserListItem)
async def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
) -> UserListItem:
    target = await session.get(User, user_id, options=[selectinload(User.roles)])
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    roles = await _load_roles_or_400(session, payload.roleIds)

    target.username = payload.username
    target.email = payload.email
    target.status = payload.status
    target.is_active = payload.status == "active"
    target.roles = roles
    session.add(target)

    try:
        await session.flush()
        await write_operation_log(
            session,
            operator_id=user.id,
            operator_name=user.username,
            module="用户管理",
            action="更新用户",
            method="PUT",
            result="成功",
            detail=f"更新用户 {target.username}",
            ip=request.client.host if request.client else "",
        )
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_user_integrity_error_message(exc))
    await session.refresh(target)
    await session.refresh(target, attribute_names=["roles"])
    return _build_user_item(target)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
) -> dict[str, str]:
    target = await session.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    try:
        delete_user_or_raise(target)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    await session.delete(target)
    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="用户管理",
        action="删除用户",
        method="DELETE",
        result="成功",
        detail=f"删除用户 {target.username}",
        ip=request.client.host if request.client else "",
    )
    await session.commit()
    return {"message": "删除成功"}


@router.patch("/{user_id}/status")
async def update_user_status(
    user_id: int,
    payload: StatusUpdateRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
) -> dict[str, str]:
    target = await session.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    target.status = payload.status
    target.is_active = payload.status == "active"
    session.add(target)

    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="用户管理",
        action="更新用户状态",
        method="PATCH",
        result="成功",
        detail=f"用户 {target.username} 状态更新为 {payload.status}",
        ip=request.client.host if request.client else "",
    )
    await session.commit()
    return {"message": "状态更新成功"}
