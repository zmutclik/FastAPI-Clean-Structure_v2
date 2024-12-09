from typing import Union, Optional
from datetime import datetime, timedelta
from fastapi import Security, Depends, HTTPException, Request, status, Response
from sqlalchemy.orm import Session

from pydantic import ValidationError, BaseModel
from jose import JWTError, jwt

from app.core.db.auth import engine_db
from app.repositories.__system__.auth import SessionRepository, ScopesRepository
from app.core import config

ALGORITHM = config.ALGORITHM
SECRET_TEXT = config.SECRET_TEXT
TOKEN_KEY = config.TOKEN_KEY


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
    scopes: list[str] = []
    cid: Optional[str] = None
    sid: Optional[str] = None


def token_decode(token, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_TEXT, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        cid: str = payload.get("cid")
        sid: str = payload.get("sid")
        if username is None:
            raise exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username, cid=cid, sid=sid)
    except (JWTError, ValidationError):
        raise credentials_exception
    return token_data


def token_create(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    print("to_encode = ", to_encode)
    if expires_delta:
        expire = datetime.now() + expires_delta
        to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_TEXT,
        algorithm=ALGORITHM,
    )
    return encoded_jwt


def user_access_token(db, userName, scopeAuth, scopeUser, timeout: int, client_id: Union[str, None] = None, session_id: Union[str, None] = None):
    scopesPass = ["default"]
    for item in scopeAuth:
        if item not in scopeUser:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user scope : " + item)
        else:
            scopesPass.append(item)
    access_token = token_create(
        data={"sub": userName, "scopes": scopesPass, "cid": client_id, "sid": session_id},
        expires_delta=timedelta(minutes=timeout),
    )
    return access_token


def user_cookie_token(
    response: Response, userName, userScopes: list[str], sessionID: int, client_id: Union[str, None] = None, session_id: Union[str, None] = None
):
    userScopes.append("default")
    userScopes.append("pages")
    access_token = token_create(
        data={"sub": userName, "scopes": userScopes, "cid": client_id, "sid": session_id},
        expires_delta=timedelta(minutes=config.TOKEN_EXPIRED),
    )
    response.set_cookie(key=TOKEN_KEY, value=access_token)
    SessionRepository().update(sessionID, {"username": userName, "EndTime": datetime.now() + timedelta(minutes=config.TOKEN_EXPIRED)})
