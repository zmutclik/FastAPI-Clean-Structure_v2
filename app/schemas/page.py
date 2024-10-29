from typing import Annotated
from fastapi import Request, HTTPException, Depends
from app.core import config
from fastapi.templating import Jinja2Templates

from app.schemas.__system__.auth import UserSchemas
from app.services.__system__.auth import get_pages_user

from sqlalchemy.orm import Session
from app.core.db.auth import engine_db
from app.repositories.__system__.auth import SessionRepository


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

    def page(self, req: Request, user: Annotated[UserSchemas, Depends(get_pages_user)]):
        self.req = req
        self.user = user
        self.initContext()

        with engine_db.begin() as connection:
            with Session(bind=connection) as db:
                SessionRepository(db).updateEndTime(req.state.sessionId)

        return req

    def pageDepends(self, req: Request, cId: str, sId: str, user: Annotated[UserSchemas, Depends(get_pages_user)]):
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
