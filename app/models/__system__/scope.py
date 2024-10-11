import os

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Time, TIMESTAMP, DateTime, func, case, Float, text
from sqlalchemy.orm import column_property, relationship, deferred, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from app.core.db import BaseAuth as Base


class ScopeTable(Base):
    __tablename__ = "scopes"

    id = Column(Integer, primary_key=True, index=True)
    scope = Column(String(32), unique=True, index=True)
    desc = Column(String(250))

    USERCOPES = relationship("UserScopeTable", back_populates="SCOPES")
