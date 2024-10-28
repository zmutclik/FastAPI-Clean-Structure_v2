from typing import Annotated
from fastapi import APIRouter, Request, Security, Depends
from sqlalchemy.orm import Session
from app.core.db.auth import get_db
from app.repositories.__system__.auth.users import UsersRepository
from app.services.__system__.auth import get_current_user
from app.schemas.__system__.auth import UserResponse

router = APIRouter(tags=["AUTH"])


@router.get("/me", response_model=UserResponse)
async def root(request: Request, current_user: Annotated[UserResponse, Security(get_current_user, scopes=[])], db: Session = Depends(get_db)):
    repo = UsersRepository(db)
    return repo.get(current_user.username)
