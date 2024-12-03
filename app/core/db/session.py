import os
from datetime import datetime

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from . import BaseSeSS as Base
from app.models.__system__ import SessionTable, SessionEndTable


now = datetime.now()
fileDB_ENGINE = "./config/_session.db"
DB_ENGINE = "sqlite:///" + fileDB_ENGINE

engine_db = create_engine(DB_ENGINE, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_db)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.rollback()
        raise
    finally:
        db.close()


if not os.path.exists(fileDB_ENGINE):
    with open(fileDB_ENGINE, "w") as f:
        f.write("")

if os.path.exists(fileDB_ENGINE):
    file_stats = os.stat(fileDB_ENGINE)
    if file_stats.st_size == 0:
        Base.metadata.create_all(bind=engine_db)
