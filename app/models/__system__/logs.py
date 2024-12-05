from sqlalchemy import Column, Integer, String, Date, Time, Float, DateTime
from app.core.db import BaseLogs as Base


class TableLogs(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    client_id = Column(String(32), index=True)
    session_id = Column(String(32), index=True)
    startTime = Column(DateTime)
    app = Column(String(100), index=True)
    platform = Column(String(100), index=True)
    browser = Column(String(100), index=True)
    referer = Column(String(500), index=True)
    path = Column(String(256), index=True)
    path_params = Column(String(256))
    method = Column(String(10), index=True)
    ipaddress = Column(String(50), index=True)
    username = Column(String(50), index=True)
    status_code = Column(Integer, index=True)
    process_time = Column(Float, nullable=True)


class TableIpAddress(Base):
    __tablename__ = "ipaddress"
    ipaddress = Column(String(50), primary_key=True, index=True)
    count = Column(Integer)
