import os

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Time, TIMESTAMP, DateTime, func, case, Float, text
from sqlalchemy.orm import column_property, relationship, deferred, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from app.core.db import BaseAuth as Base


class SessionTable(Base):
    __tablename__ = "session"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(32), index=True)
    session_id = Column(String(32), unique=True, index=True)
    username = Column(String(32), index=True)
    app = Column(String(100), index=True)
    platform = Column(String(100), index=True)
    browser = Column(String(100), index=True)
    startTime = Column(DateTime)
    EndTime = Column(DateTime)
    active = Column(Boolean, default=True)
