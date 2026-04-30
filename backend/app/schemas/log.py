from pydantic import BaseModel


class OperationLogItem(BaseModel):
    id: int
    operator: str
    module: str
    action: str
    method: str
    result: str
    time: str
    detail: str


class LoginLogItem(BaseModel):
    id: int
    username: str
    ip: str
    location: str
    device: str
    result: str
    time: str
    detail: str
