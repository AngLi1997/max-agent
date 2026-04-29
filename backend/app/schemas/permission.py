from pydantic import BaseModel


class PermissionCreateRequest(BaseModel):
    name: str
    identifier: str
    type: str
    status: str = "active"


class PermissionUpdateRequest(BaseModel):
    name: str
    identifier: str
    type: str
    status: str = "active"


class PermissionListItem(BaseModel):
    id: int
    name: str
    identifier: str
    type: str
    status: str
    createdAt: str
