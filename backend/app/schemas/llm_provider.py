from datetime import datetime

from pydantic import BaseModel


class LlmModelItem(BaseModel):
    id: int
    model_name: str
    status: str
    remark: str | None = None
    created_at: datetime


class ModelListItem(BaseModel):
    id: int
    provider_id: int
    model_name: str
    provider_type: str
    provider_api_url: str
    status: str
    remark: str | None = None
    created_at: datetime


class ModelUpdateRequest(BaseModel):
    status: str | None = None
    remark: str | None = None


class ProviderCreateRequest(BaseModel):
    type: str  # "openai" | "ollama"
    api_url: str
    api_key: str | None = None
    models: list[str]  # model names to create


class ProviderUpdateRequest(BaseModel):
    api_url: str | None = None
    api_key: str | None = None
    status: str | None = None


class ProviderItem(BaseModel):
    id: int
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


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


class ChatStreamChunk(BaseModel):
    content: str
    done: bool
