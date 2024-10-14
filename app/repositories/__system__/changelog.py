from datetime import datetime
from sqlalchemy.orm import Session
from app.models.__system__ import ChangeLogTable as MainTable
from app.schemas.__system__ import changeLogsSchemas


class ChangeLogRepository:
    def __init__(self, db_session: Session) -> None:
        self.session = db_session

    def last(self):
        d = self.session.query(MainTable).filter(MainTable.deleted_at == None).order_by(MainTable.id.desc()).first()
        return changeLogsSchemas(
            version=d.version,
            version_name=d.version_name,
            description=d.description,
        )

    def get(self, id: int):
        return self.session.query(MainTable).filter(MainTable.id == id, MainTable.deleted_at == None).first()

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

    def delete(self, username: str, id_: int) -> None:
        self.update(id_, {"deleted_at": datetime.now(), "deleted_user": username})
