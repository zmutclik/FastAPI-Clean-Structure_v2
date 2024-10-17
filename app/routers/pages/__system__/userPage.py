from typing import Annotated, Any
from enum import Enum
import datetime

from fastapi import APIRouter, Request, Security, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db.auth import engine_db, get_db
from app.schemas import PageResponseSchemas

from app.schemas.__system__.auth import UserSchemas
from app.services.__system__.auth import get_current_active_user


router = APIRouter(
    prefix="/page/users",
    tags=["FORM"],
)

pageResponse = PageResponseSchemas("templates", "pages/system/users/")
db: Session = Depends(get_db)
req_page = Annotated[PageResponseSchemas, Depends(pageResponse.page)]
req_depends = Annotated[PageResponseSchemas, Depends(pageResponse.pageDepends)]
req_nonAuth = Annotated[PageResponseSchemas, Depends(pageResponse.pageDependsNonUser)]
c_user_scope = Annotated[UserSchemas, Security(get_current_active_user, scopes=["admin"])]


class PathJS(str, Enum):
    indexJs = "index.js"
    formJs = "form.js"


###PAGES###############################################################################################################
from fastapi.responses import HTMLResponse
from app.repositories.__system__.auth import (
    UsersRepository,
    UserScopesRepository,
    ScopesRepository,
)


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def page_system_users(req: req_page):
    return pageResponse.response("index.html")


@router.get("/{cId}/{sId}/add", response_class=HTMLResponse, include_in_schema=False)
def page_system_users_form(req: req_depends, db=db):
    pageResponse.addData("userscopes", ScopesRepository(db).all())
    return pageResponse.response("form.html")


@router.get("/{cId}/{sId}/{id:int}", response_class=HTMLResponse, include_in_schema=False)
def page_system_users_form(id: int, req: req_depends, db=db):
    pageResponse.addData("userscopes", UserScopesRepository(db).getAllByUser(id))
    pageResponse.response("form.html")


@router.get("/{cId}/{sId}/{app_version}/{pathFile}", response_class=HTMLResponse, include_in_schema=False)
def page_js(req: req_nonAuth, pathFile: PathJS):
    return pageResponse.response(pathFile)


###DATATABLES##########################################################################################################
from app.models.__system__ import UsersTable
from sqlalchemy import select
from datatables import DataTable


@router.post("/{cId}/{sId}/datatables", status_code=202, include_in_schema=False)
def get_datatables(params: dict[str, Any], req: req_depends, c_user: c_user_scope) -> dict[str, Any]:
    query = select(UsersTable, UsersTable.id.label("DT_RowId")).where(UsersTable.deleted_at == None)

    datatable: DataTable = DataTable(
        request_params=params,
        table=query,
        column_names=["DT_RowId", "id", "username", "email", "full_name"],
        engine=engine_db,
        # callbacks=callbacks,
    )
    return datatable.output_result()


###CRUD################################################################################################################
from app.schemas.__system__.auth import UserResponse, UserSave, UserEdit, UserDataIn


@router.post("/{cId}/{sId}", response_model=UserResponse, status_code=201, include_in_schema=False)
async def create_user(dataIn: UserDataIn, req: req_depends, c_user: c_user_scope, db=db):
    userrepo = UsersRepository(db)
    if userrepo.get(dataIn.username):
        raise HTTPException(status_code=400, detail="USERNAME sudah ada yang menggunakan.")
    if userrepo.getByEmail(dataIn.email):
        raise HTTPException(status_code=400, detail="EMAIL sudah ada yang menggunakan.")

    data = UserSave.model_validate(dataIn.model_dump())
    data.created_user = c_user.username
    cdata = userrepo.create(data.model_dump())
    usrepo = UserScopesRepository(db)
    for i in dataIn.userScopes:
        usrepo.create({"id_user": cdata.id, "id_scope": i})
    return userrepo.get(cdata.username)


@router.post("/{cId}/{sId}/{id:int}", response_model=UserResponse, status_code=202, include_in_schema=False)
async def update_user(dataIn: UserDataIn, id: int, req: req_depends, c_user: c_user_scope, db=db):
    userrepo = UsersRepository(db)
    dataUser = userrepo.getById(id)
    if dataUser is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")

    data = UserEdit.model_validate(dataIn.model_dump())
    data.updated_at = datetime.datetime.now()
    userrepo.update(id, data.model_dump())

    usrepo = UserScopesRepository(db)
    usrepo.deleteByUser(dataUser.id)
    for i in dataIn.userScopes:
        usrepo.create({"id_user": dataUser.id, "id_scope": i})

    return userrepo.get(dataUser.username)


@router.delete(
    "/{cId}/{sId}/{id:int}",
    response_model=UserResponse,
    status_code=202,
    include_in_schema=False,
)
async def delete_user(id: int, req: req_depends, c_user: c_user_scope, db=db):
    userrepo = UsersRepository(db)
    dataUser = userrepo.getById(id)
    if dataUser is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")

    userrepo.update(
        id,
        {"deleted_at": datetime.datetime.now(), "deleted_user": c_user.username},
    )
