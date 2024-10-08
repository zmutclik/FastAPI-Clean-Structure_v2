from typing import Union, Optional, Dict
from pydantic import BaseModel
from datetime import datetime


class dataLogs(BaseModel):
    startTime: datetime
    app: str
    client_id: Union[str, None] = None
    session_id: Union[str, None] = None
    platform: str
    browser: str
    path: str
    path_params: Union[str, None] = None
    method: str
    ipaddress: str
    username: Union[str, None] = None
    status_code: Union[int, None] = None
    process_time: Union[float, None] = None


class DataTablesRequest(BaseModel):
    draw: Optional[int]
    columns: Optional[list]
    order: Optional[list]
    start: Optional[int]
    lenght: Optional[int] = None
    search: Optional[Dict]


class DataTablesRespondse(BaseModel):
    draw: Optional[int] = 1
    recordsTotal: Optional[int] = 1
    recordsFiltered: Optional[int] = 1
    data: Optional[list] = []
