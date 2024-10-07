from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
BaseLogs = declarative_base()
BaseAuth = declarative_base()

__all__ = [
    "Base",
    "BaseLogs",
    "BaseAuth",
]
