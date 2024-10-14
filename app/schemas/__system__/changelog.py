from typing import Union, Optional, Dict
from pydantic import BaseModel
from datetime import datetime


class changeLogsSchemas(BaseModel):
    version: str
    version_name: str
    description: str


class changeLogsSave(changeLogsSchemas):
    created_user: Optional[str] = None
