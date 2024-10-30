from fastapi import Request
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timedelta
from app.core.db.session import SessionTable as MainTable, SessionEndTable
from app.core import config
from app.core.db.session import get_db


class SessionEndRepository:
    def __init__(self) -> None:
        self.session: Session = get_db().__next__()

    def commit(self):
        self.session.commit()

    def create(self, dataIn: dict):
        data = SessionEndTable(**dataIn)
        self.session.add(data)


class SessionRepository:
    def __init__(self) -> None:
        self.session: Session = get_db().__next__()

    def get(self, session_id: str):
        return self.session.query(MainTable).filter(MainTable.session_id == session_id, MainTable.active == True).first()

    def getById(self, id: int):
        return self.session.query(MainTable).filter(MainTable.id == id).first()

    def allEnd(self):
        return self.session.query(MainTable).filter(or_(MainTable.EndTime < datetime.now(), MainTable.active == False)).all()

    def deleteEnd(self):
        self.session.query(MainTable).filter(or_(MainTable.EndTime < datetime.now(), MainTable.active == False)).delete(synchronize_session=False)
        self.session.commit()

    def ipaddress(self, request: Request):
        try:
            if request.headers.get("X-Real-IP") is not None:
                return request.headers.get("X-Real-IP") + " @" + request.client.host
            return request.client.host
        except:
            return request.client.host
        return ""

    def create(self, request: Request):
        dataIn = {
            "client_id": request.state.clientId,
            "session_id": request.state.sessionId,
            "username": "",
            "app": request.state.app,
            "platform": request.state.platform,
            "browser": request.state.browser,
            "startTime": datetime.now(),
            "EndTime": datetime.now() + timedelta(minutes=config.TOKEN_EXPIRED),
            "ipaddress": self.ipaddress(request),
            "active": True,
        }
        data = MainTable(**dataIn)
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data

    def update(self, id: int, dataIn: dict):
        dataIn_update = dataIn if type(dataIn) is dict else dataIn.__dict__
        (self.session.query(MainTable).filter(MainTable.id == id).update(dataIn_update))
        self.session.commit()
        return self.getById(id)

    def updateEndTime(self, session_id: str, lastPage: str):
        dataIn = {"EndTime": datetime.now() + timedelta(minutes=config.TOKEN_EXPIRED), "LastPage": lastPage}
        dataIn_update = dataIn if type(dataIn) is dict else dataIn.__dict__
        (self.session.query(MainTable).filter(MainTable.active == True, MainTable.session_id == session_id).update(dataIn_update))
        self.session.commit()

    def disable(self, session_id: str):
        dataIn = {"active": False}
        dataIn_update = dataIn if type(dataIn) is dict else dataIn.__dict__
        (self.session.query(MainTable).filter(MainTable.session_id == session_id).update(dataIn_update))
        self.session.commit()

    def migrasi(self):
        repo = SessionEndRepository()
        for item in self.allEnd():
            data = item.__dict__
            data.pop("_sa_instance_state")
            data.pop("id")
            repo.create(data)
        repo.commit()
        self.deleteEnd()
