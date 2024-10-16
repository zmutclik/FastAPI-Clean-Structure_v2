from typing import Annotated, Union, Any, Literal
from enum import Enum
import datetime

from fastapi import APIRouter, Request, Security, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.db.auth import engine_db, get_db
from app.schemas import PageResponseSchemas

from app.schemas.__system__.auth import UserSchemas
from app.services.__system__.auth import (
    page_get_current_active_user as get_user_active,
    get_current_active_user,
)


router = APIRouter(
    prefix="/page/scopes",
    tags=["FORM"],
)

pageResponse = PageResponseSchemas("templates", "pages/system/scopes/")


class PathJS(str, Enum):
    indexJs = "index.js"
    formJs = "form.js"


###PAGES###############################################################################################################
from app.repositories.__system__.auth import ScopesRepository


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def page_system_scopes(
    req: Request,
    c_user: Annotated[UserSchemas, Depends(get_user_active)],
):
    return pageResponse.response("index.html", req)


@router.get("/{cId}/{sId}/add", response_class=HTMLResponse, include_in_schema=False)
def page_system_scopes_add(
    cId: str,
    sId: str,
    req: Request,
    c_user: Annotated[UserSchemas, Depends(get_user_active)],
):
    if req.state.clientId != cId or req.state.sessionId != sId:
        raise HTTPException(status_code=404)
    pageResponse.response("form.html", req)


@router.get("/{cId}/{sId}/{id:int}", response_class=HTMLResponse, include_in_schema=False)
def page_system_scopes_form(
    cId: str,
    sId: str,
    id: int,
    req: Request,
    c_user: Annotated[UserSchemas, Depends(get_user_active)],
    db: Session = Depends(get_db),
):
    if req.state.clientId != cId or req.state.sessionId != sId:
        raise HTTPException(status_code=404)
    return pageResponse.response("form.html", req, data={"scope": ScopesRepository(db).getById(id)})


@router.get(
    "/{cId}/{sId}/{app_version}/{pathFile}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def page_js(cId: str, sId: str, req: Request, pathFile: PathJS):
    if req.state.clientId != cId or req.state.sessionId != sId:
        raise HTTPException(status_code=404)
    return pageResponse.response(pathFile, req)


###DATATABLES##########################################################################################################
from app.models.__system__ import ScopeTable
from sqlalchemy import select
from datatables import DataTable


@router.post("/{cId}/{sId}/datatables", status_code=202, include_in_schema=False)
def get_datatables(
    params: dict[str, Any],
    cId: str,
    sId: str,
    request: Request,
) -> dict[str, Any]:
    if request.state.clientId != cId or request.state.sessionId != sId:
        raise HTTPException(status_code=404)

    query = select(ScopeTable, ScopeTable.id.label("DT_RowId"))

    datatable: DataTable = DataTable(
        request_params=params,
        table=query,
        column_names=["DT_RowId", "id", "scope", "desc"],
        engine=engine_db,
        # callbacks=callbacks,
    )
    return datatable.output_result()


###CRUD################################################################################################################
from app.schemas.__system__.auth import Scopes, ScopesSave


@router.post("/{cId}/{sId}", response_model=Scopes, status_code=201, include_in_schema=False)
async def create(
    dataIn: ScopesSave,
    cId: str,
    sId: str,
    req: Request,
    current_user: Annotated[UserSchemas, Security(get_current_active_user, scopes=["admin"])],
    db: Session = Depends(get_db),
):
    if req.state.clientId != cId or req.state.sessionId != sId:
        raise HTTPException(status_code=404)

    repo = ScopesRepository(db)
    if repo.get(dataIn.scope):
        raise HTTPException(status_code=400, detail="Scope sudah ada yang menggunakan.")

    return repo.create(dataIn.model_dump())


@router.post(
    "/{cId}/{sId}/{idS}",
    response_model=Scopes,
    status_code=202,
    include_in_schema=False,
)
async def update(
    dataIn: ScopesSave,
    idS: int,
    cId: str,
    sId: str,
    req: Request,
    current_user: Annotated[UserSchemas, Security(get_current_active_user, scopes=["admin"])],
    db: Session = Depends(get_db),
):
    if req.state.clientId != cId or req.state.sessionId != sId:
        raise HTTPException(status_code=404)

    repo = ScopesRepository(db)
    data = repo.getById(idS)
    if data is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")

    return repo.update(idS, dataIn.model_dump())


@router.delete("/{cId}/{sId}/{idUser}", status_code=202, include_in_schema=False)
async def delete(
    idUser: int,
    cId: str,
    sId: str,
    req: Request,
    current_user: Annotated[UserSchemas, Security(get_current_active_user, scopes=["admin"])],
    db: Session = Depends(get_db),
):
    if req.state.clientId != cId or req.state.sessionId != sId:
        raise HTTPException(status_code=404)

    repo = ScopesRepository(db)
    data = repo.getById(idUser)
    if data is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")

    return repo.delete(idUser)
