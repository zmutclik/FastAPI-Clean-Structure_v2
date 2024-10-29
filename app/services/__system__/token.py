from typing import Union
from datetime import datetime, timedelta
from fastapi import Security, Depends, HTTPException, Request, status, Response
from sqlalchemy.orm import Session

from pydantic import ValidationError, BaseModel
from jose import JWTError, jwt

from app.core.db.auth import engine_db
from .auth_scope import verify_scope
from app.repositories.__system__.auth import ScopesRepository, SessionRepository
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


def user_access_token(userID, userName, userScope, timeout: int):
    user_scope = verify_scope(userID, userScope)
    access_token = token_create(
        data={"sub": userName, "scopes": user_scope},
        expires_delta=timedelta(minutes=timeout),
    )
    return access_token


def user_cookie_token(request: Request, response: Response, userID, userName, timeout: int, sessionID: int):
    with engine_db.begin() as connection:
        with Session(bind=connection) as db:
            userScope = []
            for item in ScopesRepository(db).getScopesUser(userID):
                userScope.append(item.scope)
            access_token = user_access_token(userID, userName, userScope, timeout)
            response.set_cookie(key=TOKEN_KEY, value=access_token)

            SessionRepository().update(sessionID, {"username": userName, "EndTime": datetime.now() + timedelta(minutes=config.TOKEN_EXPIRED)})
