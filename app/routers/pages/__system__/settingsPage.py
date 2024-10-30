from typing import Annotated, Any
from enum import Enum

from fastapi import APIRouter, Request, Security, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.db.system import engine_db, get_db
from app.schemas import PageResponseSchemas

from app.schemas.__system__.auth import UserSchemas
from app.services.__system__.auth import get_active_user


router = APIRouter(
    prefix="/systemsettings",
    tags=["FORM"],
)

pageResponse = PageResponseSchemas("templates", "pages/system/settings/")
db: Session = Depends(get_db)
req_page = Annotated[PageResponseSchemas, Depends(pageResponse.page)]
req_depends = Annotated[PageResponseSchemas, Depends(pageResponse.pageDepends)]
req_nonAuth = Annotated[PageResponseSchemas, Depends(pageResponse.pageDependsNonUser)]
c_user_scope = Annotated[UserSchemas, Security(get_active_user, scopes=["admin"])]


class PathJS(str, Enum):
    indexJs = "index.js"
    formJs = "form.js"
    changeLogJs = "form_changelog.js"
    form_cors = "form_cors.js"
    index_cors = "index_cors.js"


###PAGES###############################################################################################################
from app.repositories.__system__ import SystemRepository, ChangeLogRepository, CrossOriginRepository


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def page_system_settings(req: req_page, db=db):
    pageResponse.addData("app", SystemRepository(db).get())
    return pageResponse.response("index.html")


@router.get("/{cId}/{sId}/{app_version}/{pathFile}", response_class=HTMLResponse, include_in_schema=False)
def page_js(req: req_nonAuth, pathFile: PathJS):
    req.state.islogsave = False
    return pageResponse.response(pathFile)


###DATATABLES##########################################################################################################
from app.models.__system__ import ChangeLogTable, CrossOriginTable
from sqlalchemy import select
from datatables import DataTable


@router.post("/{cId}/{sId}/datatables", status_code=202, include_in_schema=False)
def get_datatables(params: dict[str, Any], req: req_depends, c_user: c_user_scope) -> dict[str, Any]:
    query = select(ChangeLogTable, ChangeLogTable.id.label("DT_RowId")).where(ChangeLogTable.deleted_at == None).order_by(ChangeLogTable.id.desc())

    datatable: DataTable = DataTable(
        request_params=params,
        table=query,
        column_names=["DT_RowId", "id", "datetime", "version", "version_name", "description", "created_user"],
        engine=engine_db,
        # callbacks=callbacks,
    )
    return datatable.output_result()


@router.post("/{cId}/{sId}/cors/datatables", status_code=202, include_in_schema=False)
def get_datatables_cros(params: dict[str, Any], req: req_depends, c_user: c_user_scope) -> dict[str, Any]:
    query = select(CrossOriginTable, CrossOriginTable.id.label("DT_RowId")).order_by(CrossOriginTable.id.desc())

    datatable: DataTable = DataTable(
        request_params=params,
        table=query,
        column_names=["DT_RowId", "id", "link"],
        engine=engine_db,
        # callbacks=callbacks,
    )
    return datatable.output_result()


###CRUD################################################################################################################
from app.schemas.__system__.settings import SettingsSchemas, CROSSchemas
from app.schemas.__system__.changelog import changeLogsSchemas, changeLogsSave


@router.post("/{cId}/{sId}", response_model=SettingsSchemas, status_code=202, include_in_schema=False)
async def update(dataIn: SettingsSchemas, req: req_depends, c_user: c_user_scope, db=db):
    repo = SystemRepository(db)
    data = repo.get()
    if data is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")

    return repo.update(dataIn.model_dump())


###CHANGE-LOG################################################################################################################
@router.post("/{cId}/{sId}/changelog", response_model=changeLogsSchemas, status_code=202, include_in_schema=False)
async def changelog_create(dataIn: changeLogsSchemas, req: req_depends, c_user: c_user_scope, db=db):
    repo = ChangeLogRepository(db)
    datas = changeLogsSave.model_validate(dataIn.model_dump())
    datas.created_user = c_user.username

    return repo.create(datas.model_dump())


@router.delete("/{cId}/{sId}/{id:int}", status_code=202, include_in_schema=False)
async def delete(id: int, req: req_depends, c_user: c_user_scope, db=db):
    repo = ChangeLogRepository(db)
    data = repo.get(id)
    if data is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")

    repo.delete(c_user.username, id)


###CROS################################################################################################################
@router.post("/{cId}/{sId}/cors", status_code=202, include_in_schema=False)
async def cros_create(dataIn: CROSSchemas, req: req_depends, c_user: c_user_scope, db=db):
    repo = CrossOriginRepository(db)
    return repo.create(dataIn.model_dump())


@router.delete("/{cId}/{sId}/cors/{id:int}", status_code=202, include_in_schema=False)
async def cros_delete(id: int, req: req_depends, c_user: c_user_scope, db=db):
    repo = CrossOriginRepository(db)
    data = repo.get(id)
    if data is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")

    repo.delete(id)
