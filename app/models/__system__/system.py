import os

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Date,
    Time,
    TIMESTAMP,
    DateTime,
    func,
    case,
    Float,
    text,
)
from sqlalchemy.orm import column_property, relationship, deferred, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from app.core.db import BaseSysT as Base


class SystemTable(Base):
    __tablename__ = "system"

    id = Column(Integer, primary_key=True, index=True)

    APP_NAME = Column(String(32), unique=True, index=True)
    APP_DESCRIPTION = Column(String(256))

    CLIENTID_KEY = Column(String(256))
    SESSION_KEY = Column(String(256))

    TOKEN_KEY = Column(String(256))
    TOKEN_EXPIRED = Column(Integer)

    SECRET_TEXT = Column(String(256))
    ALGORITHM = Column(String(256))

    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    created_user = Column(String(50), nullable=False)
