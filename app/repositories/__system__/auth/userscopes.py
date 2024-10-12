from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from app.core.db.auth import UserScopeTable as MainTable, ScopeTable
from .scopes import ScopesRepository


class UserScopesRepository:
    def __init__(self, db_session: Session) -> None:
        self.session: Session = db_session

    def get(self, id: int):
        return self.session.query(MainTable).filter(MainTable.id == id).first()

    def getByUser(self, id: int):
        return (
            self.session.query(MainTable)
            .join(MainTable.USER)
            .join(MainTable.SCOPES)
            .filter(MainTable.id_user == id)
            .all()
        )

    def getAllByUser(self, id_user: int):
        result = []
        byuser = self.getByUser(id_user)
        for it in ScopesRepository(self.session).all():
            d = {"id": it.id, "scope": it.scope, "checked": False}
            for i in byuser:
                if it.id == i.id_scope:
                    d["checked"] = True
            result.append(d)
        return result

    def all(self):
        return self.session.query(MainTable).all()

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
        data = self.get(id_delete)
        self.session.delete(data)
        self.session.commit()

    def deleteByUser(self, id_user: int):
        self.session.query(MainTable).filter(MainTable.id_user == id_user).delete()
        self.session.commit()
