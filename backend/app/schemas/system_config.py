from pydantic import BaseModel


class ConfigCreateRequest(BaseModel):
    name: str
    key: str
    value: str
    description: str = ""


class ConfigUpdateRequest(BaseModel):
    name: str
    key: str
    value: str
    description: str = ""


class ConfigListItem(BaseModel):
    id: int
    name: str
    key: str
    value: str
    description: str
