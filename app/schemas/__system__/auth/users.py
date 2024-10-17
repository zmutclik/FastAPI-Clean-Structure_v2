from typing import Generic, TypeVar, List, Optional, Union, Annotated, Any, Dict
from pydantic import BaseModel, Json, Field, EmailStr
from datetime import date, time, datetime

from .scope import Scopes


class UserData(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    limit_expires: Optional[int] = 30


class userloggedin(UserData):
    created_at: Optional[datetime] = None


class UserDataIn(UserData):
    userScopes: List[int]


class UserSave(UserData):
    hashed_password: Optional[str] = None
    created_user: Optional[str] = None


class UserEdit(UserData):
    full_name: str
    limit_expires: Optional[int] = 30
    updated_at: Optional[datetime] = None


class UserSchemas(UserSave):
    id: int


class GantiPassword(BaseModel):
    lama: str
    baru: str = Field(min_length=6, max_length=32)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    limit_expires: int = 30
    disabled: bool = False
    SCOPES: list[Scopes]
