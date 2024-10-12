from typing import Annotated, Union, Any, Literal
from enum import Enum
import datetime

from fastapi import APIRouter, Request, Security, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.db.auth import engine_db, get_db
from app.schemas import TemplateResponseSet


router = APIRouter(
    prefix="/page/users",
    tags=["FORM"],
)

templates = Jinja2Templates(directory="templates")
path_template = "pages/system/users/"


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
from app.schemas.__system__.auth import UserSchemas
from app.services.__system__.auth import (
    page_get_current_active_user as get_user_active,
    get_current_active_user,
)


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def page_system_users(
    req: Request,
    c_user: Annotated[UserSchemas, Depends(get_user_active)],
):
    return TemplateResponseSet(templates, path_template + "index", req)


@router.get("/{cId}/{sId}/add", response_class=HTMLResponse, include_in_schema=False)
def page_system_users_form(
    cId: str,
    sId: str,
    req: Request,
    c_user: Annotated[UserSchemas, Depends(get_user_active)],
    db: Session = Depends(get_db),
):
    if req.state.clientId != cId or req.state.sessionId != sId:
        raise HTTPException(status_code=404)
    return TemplateResponseSet(
        templates,
        path_template + "form",
        req,
        cId,
        sId,
        data={"userscopes": ScopesRepository(db).all()},
    )


@router.get(
    "/{cId}/{sId}/{id:int}", response_class=HTMLResponse, include_in_schema=False
)
def page_system_users_form(
    cId: str,
    sId: str,
    id: int,
    req: Request,
    c_user: Annotated[UserSchemas, Depends(get_user_active)],
    db: Session = Depends(get_db),
):
    if req.state.clientId != cId or req.state.sessionId != sId:
        raise HTTPException(status_code=404)
    return TemplateResponseSet(
        templates,
        path_template + "form",
        req,
        cId,
        sId,
        data={
            "user": UsersRepository(db).getById(id),
            "userscopes": UserScopesRepository(db).getAllByUser(id),
        },
    )


@router.get(
    "/{cId}/{sId}/{app_v}/{pathFile}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def page_js(cId: str, sId: str, app_v: str, req: Request, pathFile: PathJS):
    if req.state.clientId != cId or req.state.sessionId != sId:
        raise HTTPException(status_code=404)
    return TemplateResponseSet(templates, path_template + pathFile, req, cId, sId)


###DATATABLES##########################################################################################################
from app.models.__system__ import UsersTable
from sqlalchemy import select
from datatables import DataTable


@router.post("/{cId}/{sId}/datatables", status_code=202, include_in_schema=False)
def get_datatable_result(
    params: dict[str, Any],
    cId: str,
    sId: str,
    request: Request,
) -> dict[str, Any]:
    if request.state.clientId != cId or request.state.sessionId != sId:
        raise HTTPException(status_code=404)

    query = select(UsersTable, UsersTable.id.label("DT_RowId")).where(
        UsersTable.deleted_at == None
    )

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


@router.post(
    "/{cId}/{sId}",
    response_model=UserResponse,
    status_code=201,
    include_in_schema=False,
)
async def create_user(
    dataIn: UserDataIn,
    cId: str,
    sId: str,
    req: Request,
    current_user: Annotated[
        UserSchemas, Security(get_current_active_user, scopes=["admin"])
    ],
    db: Session = Depends(get_db),
):
    if req.state.clientId != cId or req.state.sessionId != sId:
        raise HTTPException(status_code=404)

    userrepo = UsersRepository(db)
    if userrepo.get(dataIn.username):
        raise HTTPException(
            status_code=400, detail="USERNAME sudah ada yang menggunakan."
        )
    if userrepo.getByEmail(dataIn.email):
        raise HTTPException(status_code=400, detail="EMAIL sudah ada yang menggunakan.")

    data = UserSave.model_validate(dataIn.model_dump())
    data.created_user = current_user.username
    cdata = userrepo.create(data.model_dump())
    usrepo = UserScopesRepository(db)
    for i in dataIn.userScopes:
        usrepo.create({"id_user": cdata.id, "id_scope": i})
    return userrepo.get(cdata.username)


@router.post(
    "/{cId}/{sId}/{idUser}",
    response_model=UserResponse,
    status_code=202,
    include_in_schema=False,
)
async def update_user(
    dataIn: UserDataIn,
    idUser: int,
    cId: str,
    sId: str,
    req: Request,
    current_user: Annotated[
        UserSchemas, Security(get_current_active_user, scopes=["admin"])
    ],
    db: Session = Depends(get_db),
):
    if req.state.clientId != cId or req.state.sessionId != sId:
        raise HTTPException(status_code=404)

    userrepo = UsersRepository(db)
    dataUser = userrepo.getById(idUser)
    if dataUser is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")

    data = UserEdit.model_validate(dataIn.model_dump())
    data.updated_at = datetime.datetime.now()
    userrepo.update(idUser, data.model_dump())

    usrepo = UserScopesRepository(db)
    usrepo.deleteByUser(dataUser.id)
    for i in dataIn.userScopes:
        usrepo.create({"id_user": dataUser.id, "id_scope": i})

    return userrepo.get(dataUser.username)


@router.delete(
    "/{cId}/{sId}/{idUser}",
    response_model=UserResponse,
    status_code=202,
    include_in_schema=False,
)
async def delete_user(
    idUser: int,
    cId: str,
    sId: str,
    req: Request,
    current_user: Annotated[
        UserSchemas, Security(get_current_active_user, scopes=["admin"])
    ],
    db: Session = Depends(get_db),
):
    if req.state.clientId != cId or req.state.sessionId != sId:
        raise HTTPException(status_code=404)

    userrepo = UsersRepository(db)
    dataUser = userrepo.getById(idUser)
    if dataUser is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")

    return userrepo.update(
        idUser,
        {"deleted_at": datetime.datetime.now(), "deleted_user": current_user.username},
    )
