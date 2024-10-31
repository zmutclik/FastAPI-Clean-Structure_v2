import os
from datetime import datetime

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from . import BaseAuth as Base
from app.models.__system__ import UsersTable, UserScopeTable
from app.models.__system__ import GroupsTable, UserGroupTable
from app.models.__system__ import ScopeTable


now = datetime.now()
fileDB_ENGINE = "./files/database/db/_auth.db"
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
        with engine_db.begin() as connection:
            with Session(bind=connection) as db:
                data = UsersTable(
                    **{
                        "username": "admin",
                        "email": "admin@test.id",
                        "full_name": "Admin SeMuT",
                        "hashed_password": "$2b$12$ofIPPqnjPf54SzEvctr3DOzNqyjZQqDaA3GraVDvBobo/UfjtGqQm",
                        "limit_expires": "525960",
                        "created_user": "sys",
                    }
                )
                db.add(data)
                db.add(ScopeTable(**{"scope": "admin", "desc": "Privilage Khusus ADMIN"}))
                db.add(UserScopeTable(**{"id_user": 1, "id_scope": 1}))
                db.add(GroupsTable(**{"group": "users", "desc": "Privilage Standart Users"}))
                db.add(GroupsTable(**{"group": "admin", "desc": "Privilage Khusus ADMIN"}))
                db.add(UserGroupTable(**{"id_user": 1, "id_group": 1}))
                db.add(UserGroupTable(**{"id_user": 1, "id_group": 2}))
                db.commit()
