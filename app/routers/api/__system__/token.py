from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.db.auth import get_db

from app.services.__system__.auth import authenticate_user, token_create
from app.schemas.__system__.auth import Token


########################################################################################################################
router = APIRouter(
    prefix="/auth",
    tags=["AUTH"],
)


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = token_create(db, user, form_data.scopes)
    return {"access_token": access_token, "token_type": "bearer"}
