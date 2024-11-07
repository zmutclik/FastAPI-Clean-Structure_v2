from typing import Annotated
from datetime import datetime, timedelta
from fastapi import Security, Depends, HTTPException, Request, status, Response
from fastapi.security import SecurityScopes
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .auth_scope import oauth2_scheme
from .token import token_decode, token_create, user_cookie_token, user_access_token
from app.core.db.auth import get_db, engine_db
from app.repositories.__system__.auth import UsersRepository, SessionRepository
from app.schemas.__system__.auth import UserResponse

from app.core import config
from app.helpers.Exceptions import RequiresLoginException

#####################################################################################################################################################


def credentials_exception(authenticate_detail: str, authenticate_value: str):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=authenticate_detail,
        headers={"WWW-Authenticate": authenticate_value},
    )


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str, db: Session):
    userrepo = UsersRepository(db)
    user = userrepo.get(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


#####################################################################################################################################################


async def get_current_user(security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)], request: Request):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    token_data = token_decode(token, credentials_exception("Could not validate credentials", authenticate_value))
    with engine_db.begin() as connection:
        with Session(bind=connection) as db:
            user = UsersRepository(db).get(token_data.username)
            if user is None:
                raise credentials_exception("Could not validate credentials", authenticate_value)
            for scope in security_scopes.scopes:
                if scope not in token_data.scopes:
                    raise credentials_exception("Not enough permissions", authenticate_value)

            request.state.username = user.username
            return user


async def get_active_user(current_user: Annotated[UserResponse, Security(get_current_user, scopes=["default"])]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_pages_user(request: Request):
    token = request.cookies.get(config.TOKEN_KEY)
    if token is None:
        raise RequiresLoginException(f"/auth/login?next=" + request.url.path)
    token_data = token_decode(token, RequiresLoginException(f"/auth/login?next=" + request.url.path))
    if not config.SESSION_DISABLE:
        clientId = request.state.clientId
        sessionId = request.state.sessionId
        sessRepo = SessionRepository()
        sess = sessRepo.get(sessionId)
        if sess is None:
            raise RequiresLoginException(f"/auth/login?next=" + request.url.path)

        if sess.client_id != clientId or sess.username != token_data.username:
            raise RequiresLoginException(f"/auth/login?next=" + request.url.path)

    with engine_db.begin() as connection:
        with Session(bind=connection) as db:
            user = UsersRepository(db).get(token_data.username)
            if user is None:
                raise RequiresLoginException(f"/auth/login?next=" + request.url.path)
            if user.disabled:
                raise RequiresLoginException(f"/auth/login?next=" + request.url.path)

            request.state.username = user.username
            return user
