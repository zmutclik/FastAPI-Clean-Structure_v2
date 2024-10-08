from typing import Generic, TypeVar, List, Optional, Union, Annotated, Any, Dict
from pydantic import BaseModel, Json, Field, EmailStr
from datetime import date, time, datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
    scopes: list[str] = []
