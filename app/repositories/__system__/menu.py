from sqlalchemy.orm import Session
from app.core.db.system import MenuTable, MenuTypeTable
from app.schemas.__system__.menu import Menus, Menu, MenuSave


class MenuRepository:
    def __init__(self, db_session: Session) -> None:
        self.session: Session = db_session

    def get(self, id: int):
        return self.session.query(MenuTable).filter(MenuTable.id == id).first()

    def get_0(self, menutype_id: int, parent_id: int = 0):
        res = []
        data = (
            self.session.query(MenuTable)
            .filter(MenuTable.menutype_id == menutype_id, MenuTable.parent_id == parent_id)
            .order_by(MenuTable.sort)
            .all()
        )
        for item in data:
            it = Menu.model_validate(item.__dict__)
            itj = it.model_dump()
            itj["children"] = []
            if self.getChildCount(item.id) > 0:
                itj["children"] = self.get_0(menutype_id, item.id)
            res.append(itj)
        return res

    def getType(self, menutype: str):
        return self.session.query(MenuTypeTable).filter(MenuTypeTable.menutype == menutype).first()

    def getTypeCount(self, menutype: int):
        return self.session.query(MenuTable).filter(MenuTable.menutype_id == menutype).count()

    def getChildCount(self, parent_id: int):
        return self.session.query(MenuTable).filter(MenuTable.parent_id == parent_id).count()

    def getTypeID(self, id: int):
        return self.session.query(MenuTypeTable).filter(MenuTypeTable.id == id).first()

    def all(self, id_menutype: int):
        return self.session.query(MenuTable).filter(MenuTable.id_menutype == id_menutype).order_by(MenuTable.sort).all()

    def allType(self):
        return self.session.query(MenuTypeTable).order_by(MenuTypeTable.menutype).all()

    def create(self, dataIn):
        data = MenuTable(**dataIn)
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data

    def createType(self, dataIn):
        data = MenuTypeTable(**dataIn)
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data

    def update(self, id: int, dataIn: dict):
        dataIn_update = dataIn if type(dataIn) is dict else dataIn.__dict__
        (self.session.query(MenuTable).filter(MenuTable.id == id).update(dataIn_update))
        self.session.commit()
        return self.get(id)

    def updateType(self, id: int, dataIn: dict):
        dataIn_update = dataIn if type(dataIn) is dict else dataIn.__dict__
        (self.session.query(MenuTypeTable).filter(MenuTypeTable.id == id).update(dataIn_update))
        self.session.commit()
        return self.getTypeID(id)

    def delete(self, id_delete: int):
        data = self.get(id_delete)
        self.session.delete(data)
        self.session.commit()

    def deleteType(self, id_delete: int):
        self.session.query(MenuTable).filter(MenuTable.id_menutype == id_delete).delete(synchronize_session=False)
        data = self.session.query(MenuTypeTable).filter(MenuTypeTable.id == id_delete).first()
        self.session.delete(data)
        self.session.commit()
