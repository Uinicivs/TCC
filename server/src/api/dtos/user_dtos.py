from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

from src.app.models.user_model import User, UserRole, AuthUser, RefreshUser


class CreateUserInDTO(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole


class ReadUserOutDTO(User):
    password: str = Field(exclude=True)


class ReadUsersOutDTO(User):
    password: str = Field(exclude=True)
    flowCount: int = Field(exclude=True)
    createdAt: datetime = Field(exclude=True)
    updatedAt: datetime = Field(exclude=True)


class LoginUserInDTO(BaseModel):
    email: EmailStr
    password: str


class LoginUserOutDTO(AuthUser):
    pass


class RefreshUserOutDTO(RefreshUser):
    pass
