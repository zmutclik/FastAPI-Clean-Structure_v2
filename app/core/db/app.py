from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core import config

# from app.models import ()

# https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_orm_textual_sql.htm
engine_db = create_engine(config.DATABASE.DB_ENGINE)
conn_db = engine_db.connect()

SessionLocal = sessionmaker(autocommit=False, autoflush=False)
SessionLocal.configure(binds={})


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
