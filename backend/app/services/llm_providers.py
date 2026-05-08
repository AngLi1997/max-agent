from typing import Sequence

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.llm_model import LlmModel
from app.models.llm_provider import LlmProvider
from app.schemas.llm_provider import FetchModelsRequest


async def fetch_remote_models(payload: FetchModelsRequest) -> list[str]:
    """Fetch available models from a provider API without persisting."""
    headers = {}
    if payload.api_key:
        headers["Authorization"] = f"Bearer {payload.api_key}"

    async with httpx.AsyncClient(timeout=30) as client:
        if payload.type == "openai":
            url = payload.api_url.rstrip("/") + "/v1/models"
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return [m["id"] for m in data.get("data", [])]

        elif payload.type == "ollama":
            url = payload.api_url.rstrip("/") + "/api/tags"
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]

        raise ValueError(f"Unsupported provider type: {payload.type}")


async def get_providers(session: AsyncSession) -> tuple[Sequence[LlmProvider], int]:
    """Get all providers with their models loaded."""
    q = (
        select(LlmProvider)
        .options(selectinload(LlmProvider.models))
        .order_by(LlmProvider.created_at.desc())
    )
    rows = (await session.scalars(q)).all()
    return rows, len(rows)


async def get_provider_by_id(session: AsyncSession, provider_id: int) -> LlmProvider | None:
    return await session.get(LlmProvider, provider_id, options=[selectinload(LlmProvider.models)])


async def create_provider(
    session: AsyncSession,
    name: str,
    type_: str,
    api_url: str,
    api_key: str | None,
    model_names: list[str],
) -> LlmProvider:
    provider = LlmProvider(
        name=name,
        type=type_,
        api_url=api_url,
        api_key=api_key,
        status="active",
    )
    session.add(provider)
    await session.flush()

    for m_name in model_names:
        model = LlmModel(
            provider_id=provider.id,
            model_name=m_name,
            status="active",
        )
        session.add(model)

    await session.refresh(provider)
    # reload with models
    return provider


async def update_provider(
    session: AsyncSession,
    provider: LlmProvider,
    name: str | None,
    api_url: str | None,
    api_key: str | None,
    status: str | None,
) -> LlmProvider:
    if name is not None:
        provider.name = name
    if api_url is not None:
        provider.api_url = api_url
    if api_key is not None:
        provider.api_key = api_key
    if status is not None:
        provider.status = status
    session.add(provider)
    await session.flush()
    # reload models
    q = select(LlmModel).where(LlmModel.provider_id == provider.id)
    models = (await session.scalars(q)).all()
    provider.models = models
    return provider


async def delete_provider(session: AsyncSession, provider: LlmProvider) -> None:
    await session.delete(provider)


async def delete_model(session: AsyncSession, model_id: int) -> LlmModel | None:
    model = await session.get(LlmModel, model_id)
    if model:
        await session.delete(model)
    return model
