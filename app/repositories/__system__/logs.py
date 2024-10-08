from datetime import datetime
from sqlalchemy.orm import Session

from app.core.db.logs import get_db
from app.models.__system__ import TableLogs as MainTable


class LogsRepository:
    def __init__(self, tahunbulan: datetime = None) -> None:
        if tahunbulan is None:
            tahunbulan = datetime.now()
        self.db: Session = get_db(tahunbulan).__next__()
        pass

    def get(self):
        pass

    def all(self):
        pass

    def create(self, dataIn):
        data = MainTable(**dataIn)
        self.db.add(data)
        self.db.commit()

    def execute(self, sql_):
        return self.db.execute(sql_)

    # def update(self):
    #     pass

    # def delete(self):
    #     pass
