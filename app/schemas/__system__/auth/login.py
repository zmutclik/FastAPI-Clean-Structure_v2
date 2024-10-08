from typing import Generic, TypeVar, List, Optional, Union, Annotated, Any, Dict
from pydantic import BaseModel, Json, Field, EmailStr
from datetime import date, time, datetime


class loginSchemas(BaseModel):
    email: EmailStr
    password: str
