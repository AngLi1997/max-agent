from __future__ import annotations

from pydantic import BaseModel


class MenuCreateRequest(BaseModel):
    name: str
    path: str
    permission: str = ""
    icon: str = ""
    component: str = ""
    sort: int = 1
    status: str = "active"
    parentId: int | None = None


class MenuUpdateRequest(BaseModel):
    name: str
    path: str
    permission: str = ""
    icon: str = ""
    component: str = ""
    sort: int = 1
    status: str = "active"
    parentId: int | None = None


class MenuTreeItem(BaseModel):
    id: int
    name: str
    path: str
    permission: str
    icon: str
    component: str
    sort: int
    status: str
    parentId: int | None
    children: list["MenuTreeItem"] = []
