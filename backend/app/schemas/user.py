from typing import Literal

from pydantic import BaseModel, EmailStr


class RoleSummary(BaseModel):
    id: int
    name: str
    code: str


class MenuSummary(BaseModel):
    id: int
    name: str
    path: str
    permission: str
    icon: str
    component: str
    sort: int
    status: str
    parentId: int | None
    children: list["MenuSummary"] = []


class CurrentUserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str
    roles: list[RoleSummary]
    permissions: list[str]
    menus: list[MenuSummary]
    mustChangePassword: bool


class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    roleIds: list[int]
    status: Literal["active", "inactive"] = "active"


class UserUpdateRequest(BaseModel):
    username: str
    email: EmailStr
    roleIds: list[int]
    status: Literal["active", "inactive"] = "active"


class UserListItem(BaseModel):
    id: int
    username: str
    email: EmailStr
    roles: list[RoleSummary]
    roleIds: list[int]
    status: str
    createdAt: str
    isBuiltin: bool


class CreateUserResponse(BaseModel):
    user: UserListItem
    temporaryPassword: str
