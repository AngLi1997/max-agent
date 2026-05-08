from datetime import datetime

from pydantic import BaseModel


class LlmModelItem(BaseModel):
    id: int
    model_name: str
    status: str
    created_at: datetime


class ProviderCreateRequest(BaseModel):
    name: str
    type: str  # "openai" | "ollama"
    api_url: str
    api_key: str | None = None
    models: list[str]  # model names to create


class ProviderUpdateRequest(BaseModel):
    name: str | None = None
    api_url: str | None = None
    api_key: str | None = None
    status: str | None = None


class ProviderItem(BaseModel):
    id: int
    name: str
    type: str
    api_url: str
    api_key: str | None
    status: str
    models: list[LlmModelItem]
    created_at: datetime
    updated_at: datetime


class FetchModelsRequest(BaseModel):
    type: str
    api_url: str
    api_key: str | None = None


class FetchModelsResponse(BaseModel):
    models: list[str]


class ChatRequest(BaseModel):
    message: str


class ChatStreamChunk(BaseModel):
    content: str
    done: bool
