import time
from datetime import datetime
import json

import string
import random

from fastapi import Request, Response
from starlette.routing import Match
from user_agents import parse

from __system__.schemas import dataLogs
from __system__.repositories import LogsRepository


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

    def generateId(self, request: Request, key: str):
        clientId = request.cookies.get(key)
        if clientId is None:
            clientId = "".join(random.choices(string.ascii_letters + string.digits, k=32))
        request.state.clientId = clientId
        return clientId

    async def start(self, request: Request):
        request.state.username = None
        client_id = request.state.clientId = self.generateId(request, self.clientId_key)
        session_id = request.state.sessionId = self.generateId(request, self.session_key)
        try:
            user_agent = parse(request.headers.get("user-agent"))
            platform = user_agent.os.family + user_agent.os.version_string
            browser = user_agent.browser.family + user_agent.browser.version_string
        except:
            platform = ""
            browser = ""
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
            ipaddress=request.client.host,
        )
        return request

    async def finish(self, request: Request, response: Response):
        self.data.username = request.state.username
        self.data.status_code = response.status_code
        self.data.process_time = time.time() - self.startTime

        response.set_cookie(key=self.clientId_key, value=self.data.client_id)
        response.set_cookie(key=self.session_key, value=self.data.session_id)

        self.repository.create(self.data.model_dump())
