import string
import random

from typing import Annotated
from datetime import datetime, timedelta

from fastapi import Depends, APIRouter, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import config
from app.core.db.auth import get_db

from app.repositories.__system__.auth import SessionRepository, SessionSchemas
from app.services.__system__.auth import authenticate_user, user_access_token
from app.schemas.__system__.auth import Token
from app.services.__system__ import LogServices


########################################################################################################################
router = APIRouter(
    prefix="/auth",
    tags=["AUTH"],
)


def ipaddress(request: Request):
    try:
        if request.headers.get("X-Real-IP") is not None:
            return request.headers.get("X-Real-IP") + " @" + request.client.host
        return request.client.host
    except:
        return request.client.host
    return ""


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], request: Request, db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    sessrepo = SessionRepository()
    schema = SessionSchemas(
        type="bearer",
        client_id="".join(random.choices(string.ascii_letters + string.digits, k=8)),
        session_id="".join(random.choices(string.ascii_letters + string.digits, k=8)),
        username=user.username,
        app=config.APP_NAME,
        platform=request.state.platform,
        browser=request.state.browser,
        startTime=datetime.now(),
        EndTime=datetime.now() + timedelta(minutes=user.limit_expires),
        LastPage="",
        ipaddress=ipaddress(request),
    )
    sess = sessrepo.create(request, schema)
    access_token = user_access_token(db, user.username, form_data.scopes, user.list_scope, user.limit_expires, sess.client_id, sess.session_id)
    return {"access_token": access_token, "token_type": "bearer"}
