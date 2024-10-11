from typing import Union, Optional, Dict
from pydantic import BaseModel
from datetime import datetime


class changeLogs(BaseModel):
    version: str
    version_name: str
    description: str