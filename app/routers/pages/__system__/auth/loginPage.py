from time import sleep
from datetime import datetime

from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core import config
from app.core.db.auth import get_db
from app.helpers.Exceptions import RequiresLoginException
from app.services.__system__ import LogServices

from app.repositories.__system__.auth import UsersRepository, SessionRepository, SessionEndRepository
from app.services.__system__.auth import authenticate_user, user_cookie_token
from app.schemas.__system__.auth import loginSchemas
from app.core import config
import threading

router = APIRouter(
    prefix="/auth",
    tags=["FORM"],
)
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
def form_login(
    request: Request,
    next: str = None,
    db: Session = Depends(get_db),
):
    sessrepo = SessionRepository()
    logs = LogServices(config.CLIENTID_KEY, config.SESSION_KEY, config.APP_NAME)
    sess = sessrepo.get(request.state.sessionId)
    if sess is None:
        logs.generateNewSession(request)
        sess = sessrepo.create(request)
    if sess.EndTime < datetime.now():
        sessrepo.update(sess.id, {"active": False})
        logs.generateNewSession(request)
        sessrepo.create(request)

    return templates.TemplateResponse(
        request=request,
        name="pages/auth/login/login.html",
        context={"app_name": config.APP_NAME, "clientId": request.state.clientId, "sessionId": request.state.sessionId, "nextpage": next},
    )


@router.get("/{clientId}/{sessionId}/login.js", include_in_schema=False)
def js_login(clientId: str, sessionId: str, request: Request, next: str = None):
    request.state.islogsave = False
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
    sleep(1)
    userrepo = UsersRepository(db)

    sess = SessionRepository().get(request.state.sessionId)
    if sess is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session Error.")
    if sess.EndTime < datetime.now():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session sudah Kadaluarsa.")

    user = userrepo.getByEmail(dataIn.email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User atau Password anda Salah.!")
    
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Mohon maaf USER tidak aktif.")

    userreal = authenticate_user(user.username, dataIn.password, db)
    if not userreal:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User atau Password anda Salah.!")

    user_cookie_token(request, response, user.id, user.username, config.TOKEN_EXPIRED, sess.id)


from app.core import config


@router.get("/logout/{username}", status_code=201, include_in_schema=False)
def ganti_password(
    res: Response,
    request: Request,
    db: Session = Depends(get_db),
):
    res.delete_cookie(key=config.SESSION_KEY)
    res.delete_cookie(key=config.TOKEN_KEY)

    SessionRepository().disable(request.state.sessionId)
    thread = threading.Thread(target=SessionRepository().migrasi())
    thread.start()

    sleep(1)
    raise RequiresLoginException(f"/auth/login")
