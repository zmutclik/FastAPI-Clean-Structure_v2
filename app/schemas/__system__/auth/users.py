from typing import Generic, TypeVar, List, Optional, Union, Annotated, Any, Dict
from pydantic import BaseModel, Json, Field, EmailStr
from datetime import date, time, datetime

from .scope import Scopes


class UserDataIn(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    limit_expires: Optional[int] = 30


class UserSave(UserDataIn):
    hashed_password: Optional[str] = None
    created_user: Optional[str] = None


class UserEdit(UserDataIn):
    full_name: str
    limit_expires: Optional[int] = 30
    updated_at: Optional[datetime] = None


class UserSchemas(UserSave):
    id: int


class UserResponse(BaseModel):
    # id: int
    username: str
    email: EmailStr
    full_name: str
    limit_expires: int = 30
    disabled: bool = False
    SCOPES: list[Scopes]
