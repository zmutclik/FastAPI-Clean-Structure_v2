from typing import Generic, TypeVar, List, Optional, Union, Annotated, Any, Dict
from pydantic import BaseModel, Json, Field, EmailStr
from datetime import date, time, datetime
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core import config
from app.core.db.auth import engine_db
from app.repositories.__system__.auth import UsersRepository
from app.schemas.__system__.auth import userloggedin
from fastapi.templating import Jinja2Templates

from app.schemas.__system__.auth import UserSchemas
from app.services.__system__.auth import page_get_current_active_user, get_current_active_user


class PageResponseSchemas:
    def __init__(self, path_Jinja2Templates: str, path_template: str):
        self.templates = Jinja2Templates(directory=path_Jinja2Templates)
        self.path = path_template
        self.context = {}
        self.user: UserSchemas = None

    def media_type(self, path: str):
        if path.find(".js") > 0:
            return "application/javascript"
        else:
            return "text/html"

    def page(self, req: Request, user: Annotated[UserSchemas, Depends(page_get_current_active_user)]):
        self.req = req
        self.user = user
        self.initContext()
        return req

    def pageDepends(self, req: Request, cId: str, sId: str, user: Annotated[UserSchemas, Depends(page_get_current_active_user)]):
        self.req = req
        self.user = user
        self.initContext()
        if req.state.clientId != cId or req.state.sessionId != sId:
            raise HTTPException(status_code=404)
        return req

    def pageDependsNonUser(self, req: Request, cId: str, sId: str):
        self.req = req
        self.initContext()
        if req.state.clientId != cId or req.state.sessionId != sId:
            raise HTTPException(status_code=404)
        return req

    def addData(self, key, value):
        self.context[key] = value

    def initContext(self):
        self.addData("app_name", config.APP_NAME)
        self.addData("app_version", config.APP_VERSION)
        self.addData("clientId", self.req.state.clientId)
        self.addData("sessionId", self.req.state.sessionId)
        self.addData("TOKEN_KEY", config.TOKEN_KEY)
        self.addData("segment", self.req.scope["route"].name)
        self.addData("userloggedin", self.user)

    def response(
        self,
        path: str,
    ):
        return self.templates.TemplateResponse(
            request=self.req,
            name=self.path + path,
            media_type=self.media_type(path),
            context=self.context,
        )
