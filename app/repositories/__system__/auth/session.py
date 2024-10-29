from fastapi import Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.db.auth import SessionTable as MainTable
from app.core import config


class SessionRepository:
    def __init__(self, db_session: Session) -> None:
        self.session: Session = db_session

    def get(self, session_id: str):
        return self.session.query(MainTable).filter(MainTable.session_id == session_id, MainTable.active == True).first()

    def getById(self, id: int):
        return self.session.query(MainTable).filter(MainTable.id == id).first()

    def all(self):
        return self.session.query(MainTable).all()

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

    def updateEndTime(self, session_id: str):
        dataIn = {"EndTime": datetime.now() + timedelta(minutes=config.TOKEN_EXPIRED)}
        dataIn_update = dataIn if type(dataIn) is dict else dataIn.__dict__
        (self.session.query(MainTable).filter(MainTable.active == True, MainTable.session_id == session_id).update(dataIn_update))
        self.session.commit()
