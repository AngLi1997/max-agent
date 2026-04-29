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
