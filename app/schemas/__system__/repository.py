from typing import Union, Optional, Dict
from pydantic import BaseModel
from datetime import datetime


class RepositoryData(BaseModel):
    name: str
    allocation: str
    datalink: str
    user: str
    password: str
    active: bool


class RepositorysSchemas(RepositoryData):
    id: int


class RepositorySave(RepositoryData):
    created_user: Optional[str] = None
