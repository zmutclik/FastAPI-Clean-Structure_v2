from datetime import datetime
from sqlalchemy.orm import Session
from app.models.__system__ import RepositoryTable as MainTable


class Repository:
    def __init__(self, db_session: Session) -> None:
        self.session = db_session

    def value(self, type: str):
        d = (
            self.session.query(MainTable)
            .filter(
                MainTable.deleted_at == None,
                MainTable.type == type,
                MainTable.active == True,
            )
            .order_by(MainTable.id.desc())
            .first()
        )
        return d.value

    def get(self, id: int):
        return (
            self.session.query(MainTable)
            .filter(MainTable.id == id, MainTable.deleted_at == None)
            .first()
        )

    # def all(self):
    #     return (
    #         self.session.query(MainTable)
    #         .filter(MainTable.deleted_at == None)
    #         .order_by(MainTable.username)
    #         .all()
    #     )

    def create(self, dataIn):
        data = MainTable(**dataIn)
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data

    def update(self, id: int, dataIn: dict):
        dataIn_update = dataIn if type(dataIn) is dict else dataIn.__dict__
        dataIn_update["updated_at"] = datetime.now()
        (self.session.query(MainTable).filter(MainTable.id == id).update(dataIn_update))
        self.session.commit()
        return self.get(id)

    def delete(self, username: str, id_: int) -> None:
        self.update(id_, {"deleted_at": datetime.now(), "deleted_user": username})
