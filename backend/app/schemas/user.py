from pydantic import BaseModel, EmailStr


class CurrentUserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str
    role: str
