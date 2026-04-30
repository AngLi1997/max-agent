from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ListResponse(BaseModel, Generic[T]):
    list: list[T]
    total: int
