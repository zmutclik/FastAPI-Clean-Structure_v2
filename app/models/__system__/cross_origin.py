import os

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Time, TIMESTAMP, DateTime, func, case, Float, text
from sqlalchemy.orm import column_property, relationship, deferred, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from app.core.db import BaseSysT as Base


class CrossOriginTable(Base):
    __tablename__ = "cors"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    link = Column(String(250), index=True)
