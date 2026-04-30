from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.system_config import SystemConfig
from app.models.user import User
from app.schemas.common import ListResponse
from app.schemas.system_config import ConfigCreateRequest, ConfigListItem, ConfigUpdateRequest
from app.services.audit import write_operation_log
from app.services.auth import current_active_user
from app.services.authorization import require_permission
from app.services.system_configs import update_config_value

router = APIRouter(prefix="/configs", tags=["configs"])


def _config_integrity_error_message(error: IntegrityError) -> str:
    detail = str(error.orig)
    if "system_config.key" in detail or "key" in detail:
        return "配置键已存在"
    return "配置数据违反唯一约束"


@router.get("/", response_model=ListResponse[ConfigListItem])
async def list_configs(
    key: str | None = None,
    session: AsyncSession = Depends(get_db_session),
    _user: User = Depends(require_permission("setting:config")),
) -> ListResponse[ConfigListItem]:
    q = select(SystemConfig)
    if key:
        q = q.where(SystemConfig.key.ilike(f"%{key}%"))
    rows = (await session.scalars(q)).all()
    items = [
        ConfigListItem(
            id=c.id,
            name=c.name,
            key=c.key,
            value=c.value,
            description=c.description,
        )
        for c in rows
    ]
    return ListResponse(list=items, total=len(items))


@router.post("/", response_model=ConfigListItem)
async def create_config(
    payload: ConfigCreateRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(require_permission("config:create")),
) -> ConfigListItem:
    config = SystemConfig(
        name=payload.name,
        key=payload.key,
        value=payload.value,
        description=payload.description,
    )
    session.add(config)
    try:
        await session.flush()
        await write_operation_log(
            session,
            operator_id=user.id,
            operator_name=user.username,
            module="系统配置",
            action="创建配置",
            method="POST",
            result="成功",
            detail=f"创建配置 {config.key}",
            ip=request.client.host if request.client else "",
        )
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_config_integrity_error_message(exc))
    await session.refresh(config)
    return ConfigListItem(
        id=config.id,
        name=config.name,
        key=config.key,
        value=config.value,
        description=config.description,
    )


@router.put("/{config_id}", response_model=ConfigListItem)
async def update_config(
    config_id: int,
    payload: ConfigUpdateRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(require_permission("config:update")),
) -> ConfigListItem:
    config = await session.get(SystemConfig, config_id)
    if config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="配置不存在")
    update_config_value(
        config,
        name=payload.name,
        key=payload.key,
        value=payload.value,
        description=payload.description,
    )
    session.add(config)
    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="系统配置",
        action="更新配置",
        method="PUT",
        result="成功",
        detail=f"更新配置 {config.key}",
        ip=request.client.host if request.client else "",
    )
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_config_integrity_error_message(exc))
    await session.refresh(config)
    return ConfigListItem(
        id=config.id,
        name=config.name,
        key=config.key,
        value=config.value,
        description=config.description,
    )


@router.delete("/{config_id}")
async def delete_config(
    config_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(require_permission("config:delete")),
) -> dict[str, str]:
    config = await session.get(SystemConfig, config_id)
    if config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="配置不存在")
    key = config.key
    await session.delete(config)
    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="系统配置",
        action="删除配置",
        method="DELETE",
        result="成功",
        detail=f"删除配置 {key}",
        ip=request.client.host if request.client else "",
    )
    await session.commit()
    return {"message": "删除成功"}
