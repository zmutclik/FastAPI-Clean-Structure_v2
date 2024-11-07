from typing import Union
from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .db.system import engine_db
from app.models.__system__ import SystemTable, ChangeLogTable, RepositoryTable, CrossOriginTable


class Config(BaseModel):
    APP_NAME: str
    APP_DESCRIPTION: str

    APP_VERSION: str

    CLIENTID_KEY: str
    SESSION_KEY: str
    TOKEN_KEY: str

    SECRET_TEXT: str
    TOKEN_EXPIRED: int
    ALGORITHM: str

    DATABASE: Union[str, None] = None
    RABBITMQ: Union[str, None] = None
    CORS: Union[list, None] = None

    SESSION_DISABLE: bool = False


def repository(db, alokasi):
    d = (
        db.query(RepositoryTable.datalink, RepositoryTable.user, RepositoryTable.password)
        .filter(
            RepositoryTable.deleted_at == None,
            RepositoryTable.allocation == alokasi,
            RepositoryTable.active == True,
        )
        .first()
    )
    if d:
        return d[0].format(user=d[1], password=d[2])


def changelogs(db):
    d = db.query(ChangeLogTable.version_name).filter(ChangeLogTable.deleted_at == None).order_by(ChangeLogTable.id.desc()).first()
    return d[0]


def crossOrigin(db):
    data = db.query(CrossOriginTable).all()
    res = []
    for item in data:
        res.append(item)
    return res


with engine_db.begin() as connection:
    with Session(bind=connection) as db:
        sys = db.query(SystemTable).first()
        config: Config = Config(
            APP_NAME=sys.APP_NAME,
            APP_DESCRIPTION=sys.APP_DESCRIPTION,
            APP_VERSION=changelogs(db),
            CLIENTID_KEY=sys.CLIENTID_KEY,
            SESSION_KEY=sys.SESSION_KEY,
            TOKEN_KEY=sys.TOKEN_KEY,
            SECRET_TEXT=sys.SECRET_TEXT,
            TOKEN_EXPIRED=sys.TOKEN_EXPIRED,
            ALGORITHM=sys.ALGORITHM,
            DATABASE=repository(db, "MariaDB"),
            RABBITMQ=repository(db, "RabbitMQ"),
            CORS=crossOrigin(db),
            SESSION_DISABLE=False,
        )
