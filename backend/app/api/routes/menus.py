from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.menu import Menu
from app.models.user import User
from app.schemas.menu import MenuCreateRequest, MenuTreeItem, MenuUpdateRequest
from app.schemas.role import StatusUpdateRequest
from app.services.audit import write_operation_log
from app.services.auth import current_active_user
from app.services.system_menus import apply_menu_status, build_menu_tree, validate_menu_parent

router = APIRouter(prefix="/menus", tags=["menus"])


@router.get("/tree", response_model=list[MenuTreeItem])
async def get_menu_tree(
    session: AsyncSession = Depends(get_db_session),
    _user: User = Depends(current_active_user),
) -> list[MenuTreeItem]:
    menus = (await session.scalars(select(Menu).order_by(Menu.sort, Menu.id))).all()
    return build_menu_tree(list(menus))


@router.post("/", response_model=MenuTreeItem)
async def create_menu(
    payload: MenuCreateRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
) -> MenuTreeItem:
    menu = Menu(
        name=payload.name,
        path=payload.path,
        permission=payload.permission,
        icon=payload.icon,
        component=payload.component,
        sort=payload.sort,
        status=payload.status,
        parent_id=payload.parentId,
    )
    existing_menus = (await session.scalars(select(Menu))).all()
    menus_by_id = {existing_menu.id: existing_menu for existing_menu in existing_menus}
    try:
        validate_menu_parent(menu_id=None, parent_id=payload.parentId, menus_by_id=menus_by_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    session.add(menu)
    await session.flush()
    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="菜单管理",
        action="创建菜单",
        method="POST",
        result="成功",
        detail=f"创建菜单 {menu.name}",
        ip=request.client.host if request.client else "",
    )
    await session.commit()
    await session.refresh(menu)
    return MenuTreeItem(
        id=menu.id,
        name=menu.name,
        path=menu.path,
        permission=menu.permission,
        icon=menu.icon,
        component=menu.component,
        sort=menu.sort,
        status=menu.status,
        parentId=menu.parent_id,
        children=[],
    )


@router.put("/{menu_id}", response_model=MenuTreeItem)
async def update_menu(
    menu_id: int,
    payload: MenuUpdateRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
) -> MenuTreeItem:
    menu = await session.get(Menu, menu_id)
    if menu is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="菜单不存在")
    existing_menus = (await session.scalars(select(Menu))).all()
    menus_by_id = {existing_menu.id: existing_menu for existing_menu in existing_menus}
    try:
        validate_menu_parent(menu_id=menu_id, parent_id=payload.parentId, menus_by_id=menus_by_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    menu.name = payload.name
    menu.path = payload.path
    menu.permission = payload.permission
    menu.icon = payload.icon
    menu.component = payload.component
    menu.sort = payload.sort
    menu.status = payload.status
    menu.parent_id = payload.parentId
    session.add(menu)
    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="菜单管理",
        action="更新菜单",
        method="PUT",
        result="成功",
        detail=f"更新菜单 {menu.name}",
        ip=request.client.host if request.client else "",
    )
    await session.commit()
    await session.refresh(menu)
    return MenuTreeItem(
        id=menu.id,
        name=menu.name,
        path=menu.path,
        permission=menu.permission,
        icon=menu.icon,
        component=menu.component,
        sort=menu.sort,
        status=menu.status,
        parentId=menu.parent_id,
        children=[],
    )


@router.delete("/{menu_id}")
async def delete_menu(
    menu_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
) -> dict[str, str]:
    menu = await session.get(Menu, menu_id)
    if menu is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="菜单不存在")
    name = menu.name
    await session.delete(menu)
    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="菜单管理",
        action="删除菜单",
        method="DELETE",
        result="成功",
        detail=f"删除菜单 {name}",
        ip=request.client.host if request.client else "",
    )
    await session.commit()
    return {"message": "删除成功"}


@router.patch("/{menu_id}/status")
async def update_menu_status(
    menu_id: int,
    payload: StatusUpdateRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
) -> dict[str, str]:
    menu = await session.get(Menu, menu_id)
    if menu is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="菜单不存在")
    apply_menu_status(menu, payload.status)
    session.add(menu)
    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="菜单管理",
        action="更新菜单状态",
        method="PATCH",
        result="成功",
        detail=f"菜单 {menu.name} 状态更新为 {payload.status}",
        ip=request.client.host if request.client else "",
    )
    await session.commit()
    return {"message": "状态更新成功"}
