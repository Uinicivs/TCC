from enum import Enum
from typing import Optional, Annotated
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field, ConfigDict, BeforeValidator


PyObjectId = Annotated[str, BeforeValidator(str)]


class UserRole(str, Enum):
    ADMIN = 'ADMIN'
    TESTER = 'TESTER'


class User(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

    id: Optional[PyObjectId] = Field(
        alias='_id',
        default=None,
        serialization_alias='id'
    )
    name: str
    email: EmailStr
    password: str
    role: UserRole
    flowCount: int = 0
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))


class AuthUser(BaseModel):
    accessToken: str
    refreshToken: str
    tokenType: str
    tokenExpires: datetime


class RefreshUser(BaseModel):
    accessToken: str
    tokenType: str
    tokenExpires: datetime
