from typing import Union
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


def token_decode(token, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_TEXT, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception

    return token_data


def token_create(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
        to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_TEXT,
        algorithm=ALGORITHM,
    )
    return encoded_jwt


def user_access_token(db, userName, scopeAuth, scopeUser, timeout: int):
    scopesPass = ["default"]
    for item in scopeAuth:
        if item not in scopeUser:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user scope : " + item)
        else:
            scopesPass.append(item)
    access_token = token_create(
        data={"sub": userName, "scopes": scopesPass},
        expires_delta=timedelta(minutes=timeout),
    )
    return access_token


def user_cookie_token(response: Response, userName, userScopes: list[str], sessionID: int):
    userScopes.append("default")
    userScopes.append("pages")
    access_token = token_create(
        data={"sub": userName, "scopes": userScopes},
        expires_delta=timedelta(minutes=config.TOKEN_EXPIRED),
    )
    response.set_cookie(key=TOKEN_KEY, value=access_token)
    SessionRepository().update(sessionID, {"username": userName, "EndTime": datetime.now() + timedelta(minutes=config.TOKEN_EXPIRED)})
