import time
from datetime import datetime, timedelta
import json
import string
import random
from typing import Union
from pydantic import BaseModel

from fastapi import Request, Response
from sqlalchemy.orm import Session
from starlette.routing import Match
from user_agents import parse

from app.repositories.__system__.logs import LogsRepository
from app.repositories.__system__.auth import SessionRepository
from app.core.db.auth import engine_db
from app.core import config


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


class LogServices:

    def __init__(self, clientId_key, session_key, APP_NAME):
        self.repository = LogsRepository()
        self.startTime = time.time()
        self.clientId_key = clientId_key
        self.session_key = session_key
        self.APP_NAME = APP_NAME

    def parse_params(self, request: Request):
        path_params = {}
        for route in request.app.router.routes:
            match, scope = route.matches(request)
            if match == Match.FULL:
                for name, value in scope["path_params"].items():
                    path_params[name] = value
        return json.dumps(path_params)

    def generateNewSession(self, request: Request):
        request.state.sessionId = self.sessionID = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        return self.sessionID

    def generateId(self, request: Request, key: str):
        id_ = request.cookies.get(key)
        if id_ is None:
            id_ = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        return id_

    def ipaddress(self, request: Request):
        try:
            if request.headers.get("X-Real-IP") is not None:
                return request.headers.get("X-Real-IP") + " @" + request.client.host
            return request.client.host
        except:
            return request.client.host
        return ""

    async def start(self, request: Request):
        request.state.username = None
        request.state.issave = True
        request.state.clientId = self.clientID = client_id = self.generateId(request, self.clientId_key)
        request.state.sessionId = self.sessionID = session_id = self.generateId(request, self.session_key)
        request.state.app = self.APP_NAME
        try:
            user_agent = parse(request.headers.get("user-agent"))
            platform = user_agent.os.family + user_agent.os.version_string
            browser = user_agent.browser.family + user_agent.browser.version_string
        except:
            platform = ""
            browser = ""

        request.state.platform = platform
        request.state.browser = browser
        self.data = dataLogs(
            startTime=datetime.fromtimestamp(self.startTime),
            app=self.APP_NAME,
            client_id=client_id,
            session_id=session_id,
            platform=platform,
            browser=browser,
            path=request.scope["path"],
            path_params=self.parse_params(request),
            method=request.method,
            ipaddress=self.ipaddress(request),
        )
        return request

    def finish(self, request: Request, response: Response):
        self.data.username = request.state.username
        self.data.status_code = response.status_code
        self.data.process_time = time.time() - self.startTime
        response.set_cookie(key=self.clientId_key, value=self.data.client_id)
        response.set_cookie(key=self.session_key, value=request.state.sessionId)

    def saveLogs(self, request):
        if request.state.issave:
            self.repository.create(self.data.model_dump())
