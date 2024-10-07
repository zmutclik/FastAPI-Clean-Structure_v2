from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import Form, Depends

from app.core.db.auth import UsersTable as MainTable


class UsersRepository:
    def __init__(self, db_session: Session) -> None:
        self.session = db_session

    def get(self, username: str):
        return self.session.query(MainTable).filter(MainTable.username == username).first()

    def getById(self, id: int):
        return self.session.query(MainTable).filter(MainTable.id == id).first()

    def getByEmail(self, email: str):
        return self.session.query(MainTable).filter(MainTable.email == email).first()

    def all(self):
        return self.session.query(MainTable).filter(MainTable.deleted_at == None).order_by(MainTable.username).all()

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
        return self.getById(id)

    def delete(self, username: str, id_delete: int) -> None:
        self.update(id_delete, {"deleted_at": datetime.now(), "deleted_user": username})
