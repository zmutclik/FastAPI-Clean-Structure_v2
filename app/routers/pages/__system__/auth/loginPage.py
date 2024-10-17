from typing import Annotated, Union
import json
from time import sleep

from fastapi import APIRouter, Request, Response, Cookie, Security, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core import config
from app.core.db.auth import get_db
from app.helpers.Exceptions import RequiresLoginException

from app.repositories.__system__.auth import UsersRepository, ScopesRepository
from app.services.__system__.auth import authenticate_user, create_cookie_access_token
from app.schemas.__system__.auth import loginSchemas

router = APIRouter(
    prefix="/auth",
    tags=["FORM"],
)
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
def form_login(request: Request, next: str = None):
    return templates.TemplateResponse(
        request=request,
        name="pages/auth/login/login.html",
        context={"app_name": config.APP_NAME, "clientId": request.state.clientId, "sessionId": request.state.sessionId, "nextpage": next},
    )


@router.get("/{clientId}/{sessionId}/login.js", include_in_schema=False)
def js_login(clientId: str, sessionId: str, request: Request, next: str = None):
    request.state.issave = False
    if next is None or next == "None":
        next = "/page/dashboard"
    if request.state.clientId == clientId and request.state.sessionId == sessionId:
        return templates.TemplateResponse(
            request=request,
            name="pages/auth/login/login.js",
            media_type="application/javascript",
            context={"clientId": request.state.clientId, "sessionId": request.state.sessionId, "nextpage": next},
        )
    else:
        raise HTTPException(status_code=404)


@router.post("/{clientId}/{sessionId}/login", status_code=201, include_in_schema=False)
def post_login(
    dataIn: loginSchemas,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    userrepo = UsersRepository(db)
    user = userrepo.getByEmail(dataIn.email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    userreal = authenticate_user(user.username, dataIn.password, db)
    if not userreal:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    sleep(1)
    create_cookie_access_token(db, response, user)


from app.core import config


@router.get("/logout/{username}", status_code=201, include_in_schema=False)
def ganti_password(res: Response):
    res.delete_cookie(key=config.SESSION_KEY)
    res.delete_cookie(key=config.TOKEN_KEY)
    sleep(1)
    raise RequiresLoginException(f"/auth/login")
