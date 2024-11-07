from typing import Annotated, Any
from enum import Enum

from fastapi import APIRouter, Security, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.db.auth import engine_db, get_db
from app.schemas import PageResponseSchemas

from app.schemas.__system__.auth import UserSchemas
from app.services.__system__.auth import get_active_user


router = APIRouter(
    prefix="/scopes",
    tags=["FORM"],
)

pageResponse = PageResponseSchemas("templates", "pages/system/scopes/")
db: Session = Depends(get_db)
req_page = Annotated[PageResponseSchemas, Depends(pageResponse.page)]
req_depends = Annotated[PageResponseSchemas, Depends(pageResponse.pageDepends)]
req_nonAuth = Annotated[PageResponseSchemas, Depends(pageResponse.pageDependsNonUser)]
c_user_scope = Annotated[UserSchemas, Security(get_active_user, scopes=["admin", "pages"])]


class PathJS(str, Enum):
    indexJs = "index.js"
    formJs = "form.js"


###PAGES###############################################################################################################
from app.repositories.__system__.auth import ScopesRepository


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def page_system_akun_scopes(req: req_page):
    return pageResponse.response("index.html")


@router.get("/{cId}/{sId}/add", response_class=HTMLResponse, include_in_schema=False)
def page_system_scopes_add(req: req_page):
    return pageResponse.response("form.html")


@router.get("/{cId}/{sId}/{id:int}", response_class=HTMLResponse, include_in_schema=False)
def page_system_scopes_form(id: int, req: req_page, db=db):
    pageResponse.addData("scope", ScopesRepository(db).getById(id))
    return pageResponse.response("form.html")


@router.get("/{cId}/{sId}/{app_version}/{pathFile}", response_class=HTMLResponse, include_in_schema=False)
def page_js(req: req_nonAuth, pathFile: PathJS):
    req.state.islogsave = False
    return pageResponse.response(pathFile)


###DATATABLES##########################################################################################################
from app.models.__system__ import ScopeTable
from sqlalchemy import select
from datatables import DataTable


@router.post("/{cId}/{sId}/datatables", status_code=202, include_in_schema=False)
def get_datatables(params: dict[str, Any], req: req_depends, c_user: c_user_scope) -> dict[str, Any]:
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
async def create(dataIn: ScopesSave, req: req_depends, c_user: c_user_scope, db=db):
    repo = ScopesRepository(db)
    if repo.get(dataIn.scope):
        raise HTTPException(status_code=400, detail="Scope sudah ada yang menggunakan.")

    return repo.create(dataIn.model_dump())


@router.post("/{cId}/{sId}/{id:int}", response_model=Scopes, status_code=202, include_in_schema=False)
async def update(dataIn: ScopesSave, id: int, req: req_depends, c_user: c_user_scope, db=db):
    repo = ScopesRepository(db)
    data = repo.getById(id)
    if data is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")

    return repo.update(id, dataIn.model_dump())


@router.delete("/{cId}/{sId}/{id:int}", status_code=202, include_in_schema=False)
async def delete(id: int, req: req_depends, c_user: c_user_scope, db=db):
    repo = ScopesRepository(db)
    data = repo.getById(id)
    if data is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")

    return repo.delete(id)
