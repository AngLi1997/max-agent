import json
from typing import Sequence

import httpx
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.llm_model import LlmModel
from app.models.llm_provider import LlmProvider
from app.schemas.llm_provider import FetchModelsRequest


def _build_llm_url(base_url: str, provider_type: str, suffix: str) -> str:
    """Build API URL: for OpenAI ensure /v1 prefix, for Ollama just append."""
    url = base_url.rstrip("/")
    if provider_type == "openai" and not url.endswith("/v1"):
        url += "/v1"
    return url + suffix


async def fetch_remote_models(payload: FetchModelsRequest) -> list[str]:
    """Fetch available models from a provider API without persisting."""
    headers = {}
    if payload.api_key:
        headers["Authorization"] = f"Bearer {payload.api_key}"

    async with httpx.AsyncClient(timeout=30) as client:
        if payload.type == "openai":
            url = _build_llm_url(payload.api_url, "openai", "/models")
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


async def get_providers(
    session: AsyncSession,
    name: str | None = None,
    type_: str | None = None,
) -> tuple[Sequence[LlmProvider], int]:
    """Get all providers with their models loaded."""
    q = (
        select(LlmProvider)
        .options(selectinload(LlmProvider.models))
        .order_by(LlmProvider.created_at.desc())
    )
    if name:
        q = q.where(LlmProvider.name.ilike(f"%{name}%"))
    if type_:
        q = q.where(LlmProvider.type == type_)
    rows = (await session.scalars(q)).all()
    return rows, len(rows)


async def get_provider_by_id(session: AsyncSession, provider_id: int) -> LlmProvider | None:
    q = select(LlmProvider).options(selectinload(LlmProvider.models)).where(LlmProvider.id == provider_id)
    return (await session.scalars(q)).first()


async def create_provider(
    session: AsyncSession,
    name: str,
    type_: str,
    api_url: str,
    api_key: str | None,
    model_names: list[str],
) -> LlmProvider:
    existing = await session.scalar(select(LlmProvider).where(LlmProvider.name == name))
    if existing:
        raise ValueError("接入点名称已存在")
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
    if name is not None and name != provider.name:
        existing = await session.scalar(select(LlmProvider).where(LlmProvider.name == name))
        if existing:
            raise ValueError("接入点名称已存在")
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


async def get_models(
    session: AsyncSession,
    name: str | None = None,
    type_: str | None = None,
) -> tuple[Sequence[dict], int]:
    """Get flat model list with provider info joined."""
    q = (
        select(LlmModel, LlmProvider.name, LlmProvider.type, LlmProvider.api_url)
        .join(LlmProvider, LlmModel.provider_id == LlmProvider.id)
        .order_by(LlmModel.created_at.desc())
    )
    if name:
        q = q.where(LlmModel.model_name.ilike(f"%{name}%"))
    if type_:
        q = q.where(LlmProvider.type == type_)

    rows = (await session.execute(q)).all()
    result = []
    for model, p_name, p_type, p_url in rows:
        result.append({
            "id": model.id,
            "provider_id": model.provider_id,
            "model_name": model.model_name,
            "provider_name": p_name,
            "provider_type": p_type,
            "provider_api_url": p_url,
            "status": model.status,
            "created_at": model.created_at,
        })
    return result, len(result)


async def update_model(
    session: AsyncSession,
    model: LlmModel,
    status: str | None,
) -> LlmModel:
    if status is not None:
        model.status = status
    session.add(model)
    await session.flush()
    return model


async def chat_with_model_stream(
    provider: LlmProvider,
    model_name: str,
    messages: list[dict],
):
    """Build and send a streaming chat request to the provider API.

    Returns an async generator yielding SSE-formatted strings.
    """
    headers = {"Content-Type": "application/json"}
    if provider.api_key:
        headers["Authorization"] = f"Bearer {provider.api_key}"

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            if provider.type == "openai":
                url = _build_llm_url(provider.api_url, "openai", "/chat/completions")
                body = {
                    "model": model_name,
                    "messages": messages,
                    "stream": True,
                }
                async with client.stream("POST", url, json=body, headers=headers) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
                            return
                        chunk = json.loads(data_str)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        yield f"data: {json.dumps({'content': content, 'done': False})}\n\n"

            elif provider.type == "ollama":
                url = provider.api_url.rstrip("/") + "/api/chat"
                body = {
                    "model": model_name,
                    "messages": messages,
                    "stream": True,
                }
                async with client.stream("POST", url, json=body, headers=headers) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if not line:
                            continue
                        chunk = json.loads(line)
                        content = chunk.get("message", {}).get("content", "")
                        done = chunk.get("done", False)
                        yield f"data: {json.dumps({'content': content, 'done': done})}\n\n"
                        if done:
                            return

            else:
                yield f"data: {json.dumps({'content': f'不支持的接入类型: {provider.type}', 'done': True})}\n\n"
    except httpx.HTTPError as e:
        yield f"data: {json.dumps({'content': f'[连接错误: {str(e)}]', 'done': True})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'content': f'[错误: {str(e)}]', 'done': True})}\n\n"
