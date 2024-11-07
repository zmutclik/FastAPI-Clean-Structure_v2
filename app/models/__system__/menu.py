import os

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Time, TIMESTAMP, DateTime, func, case, Float, text
from sqlalchemy.orm import column_property, relationship, deferred, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from app.core.db import BaseSysT as Base


class MenuTable(Base):
    __tablename__ = "menu"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    text = Column(String(32), unique=True, index=True)
    segment = Column(String(32), index=True)
    tooltip = Column(String(256))
    href = Column(String(256))
    icon = Column(String(256))
    icon_color = Column(String(32))

    sort = Column(Integer, default=0)
    menutype_id = Column(String(32), ForeignKey("menuType.id"), index=True)
    parent_id = Column(Integer, ForeignKey("menu.id"), index=True, default=0)
    disabled = Column(Boolean, default=False)

    MENUTYPE = relationship("MenuTypeTable", back_populates="MENU")
    children = relationship("MenuTable", back_populates="PARENT")
    PARENT = relationship("MenuTable", back_populates="children", remote_side=[id])


class MenuTypeTable(Base):
    __tablename__ = "menuType"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    menutype = Column(String(32), unique=True, index=True)
    desc = Column(String(256))

    MENU = relationship("MenuTable", back_populates="MENUTYPE")
