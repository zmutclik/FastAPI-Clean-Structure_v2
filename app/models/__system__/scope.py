import os

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Time, TIMESTAMP, DateTime, func, case, Float, text
from sqlalchemy.orm import column_property, relationship, deferred, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from app.core.db import BaseAuth as Base


class ScopeTable(Base):
    __tablename__ = "scopes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scope = Column(String(32), unique=True, index=True)
    desc = Column(String(250))

    USERCOPES = relationship("UserScopeTable", back_populates="SCOPES")


class UserScopeTable(Base):
    __tablename__ = "user_scopes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey("user.id"), index=True)
    id_scope = Column(Integer, ForeignKey("scopes.id"), index=True)

    USER = relationship("UsersTable", back_populates="SCOPES")
    SCOPES = relationship("ScopeTable", back_populates="USERCOPES")

    @hybrid_property
    def scope(self) -> str:
        return self.SCOPES.scope

    @hybrid_property
    def desc(self) -> str:
        return self.SCOPES.desc
