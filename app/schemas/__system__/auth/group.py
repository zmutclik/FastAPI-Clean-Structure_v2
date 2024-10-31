from typing import Generic, TypeVar, List, Optional, Union, Annotated, Any, Dict
from pydantic import BaseModel, Json, Field, EmailStr
from datetime import date, time, datetime


class Groups(BaseModel):
    id: int
    group: str
    desc: str


class GroupSave(BaseModel):
    group: str
    desc: str
