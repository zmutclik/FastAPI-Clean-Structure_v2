from typing import Annotated
from enum import Enum
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.db.auth import engine_db, get_db
from app.schemas import PageResponseSchemas

router = APIRouter(
    prefix="/page/profile",
    tags=["FORM"],
)
pageResponse = PageResponseSchemas("templates", "pages/auth/profile/")
db: Session = Depends(get_db)
req_page = Annotated[PageResponseSchemas, Depends(pageResponse.page)]
req_depends = Annotated[PageResponseSchemas, Depends(pageResponse.pageDepends)]
req_nonAuth = Annotated[PageResponseSchemas, Depends(pageResponse.pageDependsNonUser)]


class PathJS(str, Enum):
    indexJs = "ganti_password.js"


###PAGES###############################################################################################################
from app.repositories.__system__.auth import UsersRepository


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard(req: req_page, db=db):
    pageResponse.addData("data", UsersRepository(db).get(pageResponse.user.username))
    return pageResponse.response("index.html")


@router.get("/{cId}/{sId}/{app_version}/{pathFile}", response_class=HTMLResponse, include_in_schema=False)
def page_js(req: req_nonAuth, pathFile: PathJS, id: int = None):
    if id is not None:
        pageResponse.addData("id", id)
    return pageResponse.response(pathFile)


###CRUD################################################################################################################
from app.schemas.__system__.auth import UserResponse, GantiPassword
from app.services.__system__.auth.password import verify_password, get_password_hash


@router.post("/{cId}/{sId}/gantipassword/{id:int}", status_code=201, include_in_schema=False)
def ganti_password(id: int, dataIn: GantiPassword, req: req_depends, db=db):
    repo = UsersRepository(db)
    data = repo.getById(id)
    if data is None:
        raise HTTPException(status_code=400, detail="User tidak Terdaftar.")

    if not verify_password(dataIn.lama, data.hashed_password):
        raise HTTPException(status_code=400, detail="Password Lama Salah.")

    repo.update(id, {"hashed_password": get_password_hash(dataIn.baru), "updated_at": datetime.now()})
