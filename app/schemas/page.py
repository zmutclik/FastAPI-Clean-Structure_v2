from typing import Generic, TypeVar, List, Optional, Union, Annotated, Any, Dict
from pydantic import BaseModel, Json, Field, EmailStr
from datetime import date, time, datetime
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from app.core import config
from app.core.db.auth import engine_db
from app.repositories.__system__.auth import UsersRepository
from app.schemas.__system__.auth import userloggedin
from fastapi.templating import Jinja2Templates


class PageResponseSchemas:
    def __init__(self, path_Jinja2Templates: str, path_template: str):
        self.templates = Jinja2Templates(directory=path_Jinja2Templates)
        self.path = path_template

    def media_type(self, path: str):
        if path.find(".js") > 0:
            return "application/javascript"
        else:
            return "text/html"

    def get_user(self, username: str):
        if username is not None:
            with engine_db.begin() as connection:
                with Session(bind=connection) as db:
                    duser = UsersRepository(db).get(username)
                    if duser:
                        suser = userloggedin.model_validate(duser.__dict__)
                        return suser.model_dump()
        return None

    def response(
        self,
        path: str,
        req: Request,
        data: dict = {},
    ):
        context = {
            "app_name": config.APP_NAME,
            "app_version": config.APP_VERSION,
            "clientId": req.state.clientId,
            "sessionId": req.state.sessionId,
            "TOKEN_KEY": config.TOKEN_KEY,
            "segment": req.scope["route"].name,
            "userloggedin": self.get_user(req.state.username),
        }
        context.update(data)
        return self.templates.TemplateResponse(
            request=req,
            name=self.path + path,
            media_type=self.media_type(path),
            context=context,
        )
