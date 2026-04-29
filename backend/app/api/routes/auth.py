from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db_session
from app.models.menu import Menu
from app.models.role import Role
from app.models.user import User
from app.schemas.auth import ChangePasswordRequest, LoginRequest, LoginResponse
from app.schemas.user import CurrentUserResponse
from app.services.audit import write_login_log, write_operation_log
from app.services.auth import (
    SlidingRedisStrategy,
    authenticate_user,
    current_active_user,
    get_redis_strategy,
    get_user_manager,
)
from app.services.rbac import collect_user_permissions
from app.services.system_menus import build_menu_tree
from app.services.system_users import build_current_user_payload, change_own_password

router = APIRouter(prefix="/auth", tags=["auth"])


def get_bearer_token(authorization: Annotated[str | None, Header()] = None) -> str:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")
    return authorization[7:]


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
    user_manager=Depends(get_user_manager),
    strategy: SlidingRedisStrategy = Depends(get_redis_strategy),
) -> LoginResponse:
    ip = request.client.host if request.client else ""
    device = request.headers.get("user-agent", "")

    user = await authenticate_user(payload, session, user_manager)
    if user is None:
        await write_login_log(
            session,
            user_id=None,
            username=payload.username,
            ip=ip,
            device=device,
            result="失败",
            detail="用户名或密码错误",
        )
        await session.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名或密码错误")

    token = await strategy.write_token(user)
    await write_login_log(
        session,
        user_id=user.id,
        username=user.username,
        ip=ip,
        device=device,
        result="成功",
        detail="登录成功",
    )
    await session.commit()
    return LoginResponse(token=token, username=user.username)


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> CurrentUserResponse:
    full_user = await session.scalar(
        select(User)
        .options(
            selectinload(User.roles).selectinload(Role.permissions),
        )
        .where(User.id == user.id)
    )
    if full_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # Load ALL menus flat — avoids async lazy-loading and supports arbitrary depth
    all_menus = (await session.scalars(select(Menu).order_by(Menu.sort, Menu.id))).all()

    permissions = collect_user_permissions(full_user)

    # Build full tree from flat list, then filter by permissions
    full_tree = build_menu_tree(list(all_menus))

    def _filter_tree(items) -> list[dict]:
        result = []
        for item in items:
            children = _filter_tree(item.children)
            visible = (
                item.status == "active"
                and (not item.permission or item.permission in permissions or bool(children))
            )
            if not visible:
                continue
            result.append(
                {
                    "id": item.id,
                    "name": item.name,
                    "path": item.path,
                    "permission": item.permission,
                    "icon": item.icon,
                    "component": item.component,
                    "sort": item.sort,
                    "status": item.status,
                    "parentId": item.parentId,
                    "children": children,
                }
            )
        return result

    menus = _filter_tree(full_tree)
    roles = [{"id": r.id, "name": r.name, "code": r.code} for r in full_user.roles]
    payload = build_current_user_payload(
        user=full_user,
        roles=roles,
        permissions=permissions,
        menus=menus,
    )
    return CurrentUserResponse(**payload)


@router.post("/logout")
async def logout(
    request: Request,
    token: str = Depends(get_bearer_token),
    user: User = Depends(current_active_user),
    strategy: SlidingRedisStrategy = Depends(get_redis_strategy),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    ip = request.client.host if request.client else ""
    device = request.headers.get("user-agent", "")
    await strategy.destroy_token(token, user)
    await write_login_log(
        session,
        user_id=user.id,
        username=user.username,
        ip=ip,
        device=device,
        result="退出",
        detail="用户退出登录",
    )
    await session.commit()
    return {"message": "退出成功"}


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    try:
        change_own_password(user, old_password=payload.oldPassword, new_password=payload.newPassword)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    session.add(user)
    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="用户管理",
        action="修改本人密码",
        method="POST",
        result="成功",
        detail=f"用户 {user.username} 修改了自己的密码",
        ip="",
    )
    await session.commit()
    return {"message": "密码修改成功"}
