from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from app.core.db.auth import engine_db
from app.repositories.__system__.auth import ScopesRepository

ScopeList = {}
with engine_db.begin() as connection:
    with Session(bind=connection) as db:
        scope = ScopesRepository(db)
        for item in scope.all():
            ScopeList[item.scope] = item.desc

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
    scopes=ScopeList,
)