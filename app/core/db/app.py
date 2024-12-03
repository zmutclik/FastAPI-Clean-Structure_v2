from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from app.core import config


try:
    # https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_orm_textual_sql.htm
    engine_db = create_engine(config.DATABASE)
    conn_db = engine_db.connect()

    SessionLocal = sessionmaker(autocommit=False, autoflush=False)
    SessionLocal.configure(
        binds={
            #############################################
        }
    )
    if not engine_db.dialect.has_table(table_name="repository", connection=conn_db):
        from . import Base

        Base.metadata.create_all(bind=engine_db)
        # with engine_db.begin() as connection:
        #     with Session(bind=connection) as db:
        #         db.add(RefServerTable(**{"name": "local", "metode": "local", "path": "files/database/json", "created_user": "init"}))
        #         db.commit()

except OperationalError as err:
    if "1045" in err.args[0]:
        print("Access Denied")
    elif "2003" in err.args[0]:
        print("Connection Refused")
    else:
        raise


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
