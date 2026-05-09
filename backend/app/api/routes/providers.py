from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db_session
from app.models.llm_model import LlmModel
from app.models.llm_provider import LlmProvider
from app.models.user import User
from app.schemas.common import ListResponse
from app.schemas.llm_provider import (
    ChatRequest,
    FetchModelsRequest,
    FetchModelsResponse,
    LlmModelItem,
    ModelListItem,
    ModelUpdateRequest,
    ProviderCreateRequest,
    ProviderItem,
    ProviderUpdateRequest,
)
from app.services.audit import write_operation_log
from app.services.authorization import require_permission
from app.services.llm_providers import (
    chat_with_model_stream,
    create_provider,
    delete_model,
    delete_provider,
    fetch_remote_models,
    get_models,
    get_provider_by_id,
    get_providers,
    update_model,
    update_provider,
)
from app.utils.request import get_client_ip

router = APIRouter(prefix="/providers", tags=["providers"])


def _mask_api_key(key: str | None) -> str | None:
    if not key:
        return None
    if len(key) <= 8:
        return key[:2] + "****"
    return key[:4] + "****" + key[-4:]


def _provider_to_item(provider: LlmProvider) -> ProviderItem:
    return ProviderItem(
        id=provider.id,
        type=provider.type,
        api_url=provider.api_url,
        api_key=_mask_api_key(provider.api_key),
        status=provider.status,
        models=[
            LlmModelItem(
                id=m.id,
                model_name=m.model_name,
                status=m.status,
                remark=m.remark,
                created_at=m.created_at,
            )
            for m in (provider.models or [])
        ],
        created_at=provider.created_at,
        updated_at=provider.updated_at,
    )


@router.get("/", response_model=ListResponse[ProviderItem])
async def list_providers(
    type: str | None = None,
    session: AsyncSession = Depends(get_db_session),
    _user: User = Depends(require_permission("model:view")),
) -> ListResponse[ProviderItem]:
    rows, total = await get_providers(session, type_=type)
    return ListResponse(list=[_provider_to_item(r) for r in rows], total=total)


@router.get("/models", response_model=ListResponse[ModelListItem])
async def list_models(
    name: str | None = None,
    type: str | None = None,
    session: AsyncSession = Depends(get_db_session),
    _user: User = Depends(require_permission("model:view")),
) -> ListResponse[ModelListItem]:
    rows, total = await get_models(session, name=name, type_=type)
    return ListResponse(list=[ModelListItem(**r) for r in rows], total=total)


@router.get("/{provider_id}", response_model=ProviderItem)
async def get_provider(
    provider_id: int,
    session: AsyncSession = Depends(get_db_session),
    _user: User = Depends(require_permission("model:view")),
) -> ProviderItem:
    provider = await get_provider_by_id(session, provider_id)
    if not provider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="接入点不存在")
    return _provider_to_item(provider)


@router.post("/", response_model=ProviderItem, status_code=status.HTTP_201_CREATED)
async def create_provider_endpoint(
    payload: ProviderCreateRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(require_permission("model:create")),
) -> ProviderItem:
    if not payload.models:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请至少选择一个模型")
    try:
        provider = await create_provider(
            session,
            type_=payload.type,
            api_url=payload.api_url,
            api_key=payload.api_key,
            model_names=payload.models,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="模型管理",
        action="创建接入点",
        method="POST",
        result="成功",
        detail=f"创建接入点 ({payload.type}/{payload.api_url})",
        ip=get_client_ip(request),
    )
    await session.commit()
    provider = await get_provider_by_id(session, provider.id)
    return _provider_to_item(provider)


@router.put("/{provider_id}", response_model=ProviderItem)
async def update_provider_endpoint(
    provider_id: int,
    payload: ProviderUpdateRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(require_permission("model:update")),
) -> ProviderItem:
    provider = await get_provider_by_id(session, provider_id)
    if not provider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="接入点不存在")
    try:
        provider = await update_provider(
            session, provider,
            api_url=payload.api_url,
            api_key=payload.api_key,
            status=payload.status,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="模型管理",
        action="更新接入点",
        method="PUT",
        result="成功",
        detail=f"更新接入点 ({provider.type}/{provider.api_url})",
        ip=get_client_ip(request),
    )
    await session.commit()
    provider = await get_provider_by_id(session, provider.id)
    return _provider_to_item(provider)


@router.delete("/{provider_id}")
async def delete_provider_endpoint(
    provider_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(require_permission("model:delete")),
) -> dict[str, str]:
    provider = await get_provider_by_id(session, provider_id)
    if not provider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="接入点不存在")
    label = f"{provider.type}/{provider.api_url}"
    await delete_provider(session, provider)
    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="模型管理",
        action="删除接入点",
        method="DELETE",
        result="成功",
        detail=f"删除接入点 ({label})",
        ip=get_client_ip(request),
    )
    await session.commit()
    return {"message": "删除成功"}


@router.post("/fetch-models", response_model=FetchModelsResponse)
async def fetch_models(
    payload: FetchModelsRequest,
    _user: User = Depends(require_permission("model:create")),
) -> FetchModelsResponse:
    try:
        models = await fetch_remote_models(payload)
        return FetchModelsResponse(models=models)
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"无法连接到 API 地址: {str(e)}",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/models/{model_id}")
async def delete_model_endpoint(
    model_id: int,
    session: AsyncSession = Depends(get_db_session),
    _user: User = Depends(require_permission("model:update")),
) -> dict[str, str]:
    model = await delete_model(session, model_id)
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模型不存在")
    await session.commit()
    return {"message": "删除成功"}


@router.put("/models/{model_id}")
async def update_model_endpoint(
    model_id: int,
    payload: ModelUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    _user: User = Depends(require_permission("model:update")),
) -> dict[str, str]:
    model = await session.get(LlmModel, model_id)
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模型不存在")
    await update_model(session, model, status=payload.status, remark=payload.remark)
    await session.commit()
    return {"message": "更新成功"}


@router.post("/models/{model_id}/chat")
async def chat_with_model(
    model_id: int,
    payload: ChatRequest,
    session: AsyncSession = Depends(get_db_session),
    _user: User = Depends(require_permission("model:view")),
) -> StreamingResponse:
    q = (
        select(LlmModel)
        .options(selectinload(LlmModel.provider))
        .where(LlmModel.id == model_id)
    )
    model = (await session.scalars(q)).first()
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模型不存在")
    if not model.provider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="关联接入点不存在")

    return StreamingResponse(
        chat_with_model_stream(model.provider, model.model_name, [m.model_dump() for m in payload.messages]),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
