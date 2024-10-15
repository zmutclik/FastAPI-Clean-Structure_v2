from typing import Annotated, Union
import json
from time import sleep

from fastapi import APIRouter, Request, Response, Cookie, Security, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core import config
from app.schemas.__system__.auth import UserSchemas
from app.services.__system__.auth import page_get_current_active_user as get_user_active

router = APIRouter(
    prefix="/page/documentation",
    tags=["FORM"],
)
templates = Jinja2Templates(directory="templates")


@router.get("", response_class=HTMLResponse, include_in_schema=False)
def documentation_page(
    request: Request,
    current_user: Annotated[UserSchemas, Depends(get_user_active)],
):
    return templates.TemplateResponse(
        request=request,
        name="pages/documentation.html",
        context={
            "app_name": config.APP_NAME,
            "clientId": request.state.clientId,
            "sessionId": request.state.sessionId,
            "segment": request.scope["route"].name,
        },
    )
