import json
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


def _build_openai_messages(user_message: str) -> list[dict]:
    return [{"role": "user", "content": user_message}]


def _build_ollama_messages(user_message: str) -> list[dict]:
    return [{"role": "user", "content": user_message}]


async def chat_with_model_stream(
    provider: LlmProvider,
    model_name: str,
    user_message: str,
):
    """Build and send a streaming chat request to the provider API.

    Returns an async generator yielding SSE-formatted strings.
    """
    headers = {"Content-Type": "application/json"}
    if provider.api_key:
        headers["Authorization"] = f"Bearer {provider.api_key}"

    async with httpx.AsyncClient(timeout=60) as client:
        if provider.type == "openai":
            url = provider.api_url.rstrip("/") + "/v1/chat/completions"
            body = {
                "model": model_name,
                "messages": _build_openai_messages(user_message),
                "stream": True,
            }
            async with client.stream("POST", url, json=body, headers=headers) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        yield json.dumps({"content": "", "done": True})
                        return
                    chunk = json.loads(data_str)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    yield json.dumps({"content": content, "done": False})

        elif provider.type == "ollama":
            url = provider.api_url.rstrip("/") + "/api/chat"
            body = {
                "model": model_name,
                "messages": _build_ollama_messages(user_message),
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
                    yield json.dumps({"content": content, "done": done})
                    if done:
                        return

        else:
            raise ValueError(f"Unsupported provider type: {provider.type}")
