from typing import Union, Optional, Dict
from pydantic import BaseModel
from datetime import datetime


class RepositoryData(BaseModel):
    name: str
    type: str
    value: str
    active: bool


class RepositorysSchemas(RepositoryData):
    id: int


class RepositorySave(RepositoryData):
    created_user: Optional[str] = None
