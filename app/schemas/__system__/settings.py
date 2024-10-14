from typing import Union, Optional, Dict
from pydantic import BaseModel
from datetime import datetime


class SettingsSchemas(BaseModel):
    APP_NAME: str
    APP_DESCRIPTION: str

    CLIENTID_KEY: str
    SESSION_KEY: str

    TOKEN_KEY: str
    TOKEN_EXPIRED: int
    SECRET_TEXT: str
    ALGORITHM: str
