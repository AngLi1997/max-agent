from pydantic import BaseModel


class RoleCreateRequest(BaseModel):
    name: str
    code: str
    description: str = ""
    status: str = "active"


class RoleUpdateRequest(BaseModel):
    name: str
    code: str
    description: str = ""
    status: str = "active"


class RoleListItem(BaseModel):
    id: int
    name: str
    code: str
    description: str
    status: str
    isBuiltin: bool
    createdAt: str


class RolePermissionAssignRequest(BaseModel):
    permissionIds: list[int]


class StatusUpdateRequest(BaseModel):
    status: str
