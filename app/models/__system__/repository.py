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


class RepositoryTable(Base):
    __tablename__ = "repository"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(32), index=True)
    type = Column(String(32), index=True)
    value = Column(String(256))
    active = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    created_user = Column(String(50), nullable=False)
    deleted_user = Column(String(50))
