import os
from datetime import datetime

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from . import BaseSysT as Base
from app.models.__system__ import SystemTable, ChangeLogTable, RepositoryTable, CrossOriginTable, MenuTable, MenuTypeTable


DB_FILE = "./config/_system.db"
DB_ENGINE = "sqlite:///" + DB_FILE

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


if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        f.write("")

if os.path.exists(DB_FILE):
    file_stats = os.stat(DB_FILE)
    if file_stats.st_size == 0:
        Base.metadata.create_all(bind=engine_db)
        with engine_db.begin() as connection:
            with Session(bind=connection) as db:
                import random
                import string

                letters = string.ascii_uppercase + string.ascii_letters + string.digits + string.ascii_lowercase
                SECRET_TEXT = "".join(random.choice(letters) for i in range(32))
                db.add(
                    SystemTable(
                        **{
                            "id": 1,
                            "APP_NAME": "FastAPI cleanStructure",
                            "APP_DESCRIPTION": "This is a very fancy project, with auto docs for the API and everything.",
                            "CLIENTID_KEY": "fastapi-clean-structure_id",
                            "SESSION_KEY": "fastapi-clean-structure_sesi",
                            "TOKEN_KEY": "fastapi-clean-structure_token",
                            "TOKEN_EXPIRED": 30,
                            "SECRET_TEXT": SECRET_TEXT,
                            "ALGORITHM": "HS256",
                            "created_user": "SeMuT CiLiK",
                        }
                    )
                )
                db.add(
                    ChangeLogTable(
                        **{
                            "version": "0.001",
                            "version_name": "init",
                            "description": "Initial Commit",
                            "created_user": "SeMuT CiLiK",
                        }
                    )
                )
                db.add(
                    RepositoryTable(
                        **{
                            "name": "MariaDB",
                            "allocation": "MariaDB",
                            "datalink": "mysql+pymysql://{user}:{password}@127.0.0.1:3307/db",
                            "user": "root",
                            "password": "password",
                            "active": True,
                            "created_user": "SeMuT CiLiK",
                        }
                    )
                )
                db.add(
                    RepositoryTable(
                        **{
                            "name": "RabbitMQ",
                            "allocation": "RabbitMQ",
                            "datalink": "amqp://{user}:{password}@192.168.40.5:5672//semut-dev",
                            "user": "guest",
                            "password": "guest",
                            "active": True,
                            "created_user": "SeMuT CiLiK",
                        }
                    )
                )
                db.add(CrossOriginTable(**{"link": "http://localhost"}))
                db.add(CrossOriginTable(**{"link": "http://127.0.0.1"}))
                db.add(CrossOriginTable(**{"link": "http://0.0.0.0"}))
                db.add(CrossOriginTable(**{"link": "http://127.0.0.1:8001"}))

                db.add(MenuTypeTable(**{"menutype": "sidebar", "desc": "Side Bar Menu"}))
                db.add(
                    MenuTable(
                        **{
                            "text": "Dashboard",
                            "href": "/page/dashboard",
                            "segment": "dashboard",
                            "icon": "fas fa-tachometer-alt",
                            "icon_color": "",
                            "sort": 1,
                            "menutype_id": 1,
                            "parent_id": 0,
                        }
                    )
                )
                db.add(
                    MenuTable(
                        **{
                            "text": "System",
                            "segment": "system",
                            "href": "#",
                            "icon": "fas fa-cogs",
                            "icon_color": "",
                            "sort": 2,
                            "menutype_id": 1,
                            "parent_id": 0,
                        }
                    )
                )
                db.add(
                    MenuTable(
                        **{
                            "text": "Akun",
                            "segment": "users",
                            "href": "/page/sys/users/",
                            "icon_color": "",
                            "icon": "fas fa-house-user",
                            "sort": 1,
                            "menutype_id": 1,
                            "parent_id": 2,
                        }
                    )
                )
                db.add(
                    MenuTable(
                        **{
                            "text": "Menu",
                            "segment": "menu",
                            "href": "/page/sys/menu/",
                            "icon_color": "",
                            "icon": "fas fa-list-alt",
                            "sort": 2,
                            "menutype_id": 1,
                            "parent_id": 2,
                        }
                    )
                )
                db.add(
                    MenuTable(
                        **{
                            "text": "Scope",
                            "segment": "scope",
                            "href": "/page/sys/scopes/",
                            "icon": "fas fa-map-marker-alt",
                            "icon_color": "",
                            "sort": 3,
                            "menutype_id": 1,
                            "parent_id": 2,
                        }
                    )
                )
                db.add(
                    MenuTable(
                        **{
                            "text": "Group",
                            "segment": "group",
                            "href": "/page/sys/groups/",
                            "icon": "fas fa-object-group",
                            "icon_color": "",
                            "sort": 4,
                            "menutype_id": 1,
                            "parent_id": 2,
                        }
                    )
                )
                db.add(
                    MenuTable(
                        **{
                            "text": "Gudang Link",
                            "segment": "repository",
                            "href": "/page/sys/repository/",
                            "icon": "fas fa-link",
                            "icon_color": "",
                            "sort": 5,
                            "menutype_id": 1,
                            "parent_id": 2,
                        }
                    )
                )
                db.add(
                    MenuTable(
                        **{
                            "text": "Setting Sistem",
                            "segment": "setting",
                            "href": "/page/sys/systemsettings/",
                            "icon": "fas fa-headset",
                            "icon_color": "",
                            "sort": 6,
                            "menutype_id": 1,
                            "parent_id": 2,
                        }
                    )
                )
                db.add(
                    MenuTable(
                        **{
                            "text": "Logs",
                            "segment": "logs",
                            "href": "/page/sys/logs/",
                            "icon": "fas fa-map-marked-alt",
                            "icon_color": "",
                            "sort": 7,
                            "menutype_id": 1,
                            "parent_id": 2,
                        }
                    )
                )
                db.add(
                    MenuTable(
                        **{
                            "text": "Session",
                            "segment": "session",
                            "href": "/page/sys/session/",
                            "icon": "fas fa-door-open",
                            "icon_color": "",
                            "sort": 8,
                            "menutype_id": 1,
                            "parent_id": 2,
                        }
                    )
                )
                db.add(
                    MenuTable(
                        **{
                            "text": "Documentation",
                            "segment": "documentation",
                            "href": "/page/documentation",
                            "icon": "fas fa-file-code",
                            "icon_color": "",
                            "sort": 3,
                            "menutype_id": 1,
                            "parent_id": 0,
                        }
                    )
                )
                db.commit()
