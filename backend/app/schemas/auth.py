from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    username: str


class ChangePasswordRequest(BaseModel):
    oldPassword: str
    newPassword: str
