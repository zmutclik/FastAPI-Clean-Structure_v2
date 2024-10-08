from typing import Generic, TypeVar, List, Optional, Union, Annotated, Any, Dict
from pydantic import BaseModel, Json, Field, EmailStr
from datetime import date, time, datetime


class Scopes(BaseModel):
    id: int
    scope: str
    desc: str
    
class UserScopesSave(BaseModel):
    id_user: int
    id_scope: int
    
    
class ScopesSave(BaseModel):
    scope: str
    desc: str