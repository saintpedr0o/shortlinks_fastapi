from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr, Field


class BaseUser(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr


class UserCreate(BaseUser):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    login: str | EmailStr = Field(
        ...,
        json_schema_extra={"example": "Username or email"},
    )
    password: str = Field(
        ...,
        json_schema_extra={"example": "mypassword123"},
    )


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    model_config = {"from_attributes": True}


class UserAdminUpdate(UserUpdate):
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserOut(BaseUser):
    id: uuid.UUID
    is_active: bool
    is_superuser: bool

    model_config = {"from_attributes": True}
