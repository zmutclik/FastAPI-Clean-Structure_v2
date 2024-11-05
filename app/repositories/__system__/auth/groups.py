from sqlalchemy.orm import Session
from app.core.db.auth import GroupsTable as MainTable


class GroupsRepository:
    def __init__(self, db_session: Session) -> None:
        self.session: Session = db_session

    def get(self, group: str):
        return self.session.query(MainTable).filter(MainTable.group == group).first()

    def getById(self, id: int):
        return self.session.query(MainTable).filter(MainTable.id == id).first()

    def all(self):
        return self.session.query(MainTable).order_by(MainTable.group).all()

    def list_user_checked(self, userGroups: list):
        result = []
        for it in self.all():
            d = {"id": it.id, "group": it.group, "checked": False}
            if it.group in userGroups:
                d["checked"] = True
            result.append(d)
        return result

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

    def delete(self, id_delete: int):
        data = self.getById(id_delete)
        self.session.delete(data)
        self.session.commit()
