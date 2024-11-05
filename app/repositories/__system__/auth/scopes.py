from sqlalchemy.orm import Session
from app.core.db.auth import ScopeTable as MainTable


class ScopesRepository:
    def __init__(self, db_session: Session) -> None:
        self.session: Session = db_session

    def get(self, scope: str):
        return self.session.query(MainTable).filter(MainTable.scope == scope).first()

    def getById(self, id: int):
        return self.session.query(MainTable).filter(MainTable.id == id).first()

    def all(self):
        return self.session.query(MainTable).order_by(MainTable.scope).all()

    def list_user_checked(self, userGroups: list):
        result = []
        for it in self.all():
            d = {"id": it.id, "scope": it.scope, "checked": False}
            if it.scope in userGroups:
                d["checked"] = True
            result.append(d)
        return result

    def list(self):
        res = []
        for item in self.all():
            res.append(item.scope)
        return res

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
