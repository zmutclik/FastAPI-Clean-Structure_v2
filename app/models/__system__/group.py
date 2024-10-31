import os

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Time, TIMESTAMP, DateTime, func, case, Float, text
from sqlalchemy.orm import column_property, relationship, deferred, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from app.core.db import BaseAuth as Base


class GroupsTable(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    group = Column(String(64), unique=True, index=True)
    desc = Column(String(256))

    USERGROUPS = relationship("UserGroupTable", back_populates="GROUPS")


class UserGroupTable(Base):
    __tablename__ = "user_groups"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("user.id"), index=True)
    id_group = Column(Integer, ForeignKey("groups.id"), index=True)

    USER = relationship("UsersTable", back_populates="GROUPS")
    GROUPS = relationship("GroupsTable", back_populates="USERGROUPS")

    @hybrid_property
    def group(self) -> str:
        return self.GROUPS.group

    @hybrid_property
    def desc(self) -> str:
        return self.GROUPS.desc
