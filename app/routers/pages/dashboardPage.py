from typing import Annotated, Union
import json
from time import sleep

from fastapi import (
    APIRouter,
    Request,
    Response,
    Cookie,
    Security,
    Depends,
    HTTPException,
    status,
)
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core import config
from app.schemas import PageResponseSchemas
from app.schemas.__system__.auth import UserSchemas
from app.services.__system__.auth import page_get_current_active_user as get_user_active

router = APIRouter(
    prefix="/page",
    tags=["FORM"],
)
pageResponse = PageResponseSchemas("templates", "pages/dashboard/")


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def dashboard(
    request: Request,
    current_user: Annotated[UserSchemas, Depends(get_user_active)],
):
    return pageResponse.response("index2.html", request)
