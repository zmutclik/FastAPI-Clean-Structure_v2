import os

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Time, TIMESTAMP, DateTime, func, case, Float, text
from sqlalchemy.orm import column_property, relationship, deferred, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from app.core.db import BaseAuth as Base


class UsersTable(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(32), unique=True, index=True)
    email = Column(String(50), unique=True, index=True)
    full_name = Column(String(50))
    hashed_password = Column(String(256))
    limit_expires = Column(Integer, default=30)
    disabled = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    created_user = Column(String(50), nullable=False)
    deleted_user = Column(String(50))

    SCOPES = relationship("UserScopeTable", back_populates="USER")
    GROUPS = relationship("UserGroupTable", back_populates="USER")

    @hybrid_property
    def list_scope(self) -> list[int]:
        res = []
        for item in self.SCOPES:
            res.append(item.scope)
        return res

    @hybrid_property
    def list_group(self) -> list[int]:
        res = []
        for item in self.GROUPS:
            res.append(item.group)
        return res
