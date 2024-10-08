from datetime import datetime, timedelta
from typing import Union, Annotated
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.core import config


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
        to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        config.SECRET_TEXT,
        algorithm=config.ALGORITHM,
    )
    return encoded_jwt