from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import Form, Depends

from app.core.db.system import SystemTable as MainTable


class SystemRepository:
    def __init__(self, db_session: Session) -> None:
        self.session = db_session

    def get(self):
        return self.session.query(MainTable).first()

    def update(self, dataIn: dict):
        dataIn_update = dataIn if type(dataIn) is dict else dataIn.__dict__
        (self.session.query(MainTable).filter(MainTable.id == 1).update(dataIn_update))
        self.session.commit()
        return self.get()
