from datetime import datetime
from sqlalchemy.orm import Session
from app.models.__system__ import CrossOriginTable as MainTable


class CrossOriginRepository:
    def __init__(self, db_session: Session) -> None:
        self.session = db_session

    def get(self, id: int):
        return self.session.query(MainTable).filter(MainTable.id == id).first()

    def create(self, dataIn):
        data = MainTable(**dataIn)
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data

    def update(self, id: int, dataIn: dict):
        dataIn_update = dataIn if type(dataIn) is dict else dataIn.__dict__
        (self.session.query(MainTable).filter(MainTable.id == id).update(dataIn_update))
        self.session.commit()

    def delete(self, id: int) -> None:
        data = self.get(id)
        self.session.delete(data)
        self.session.commit()
