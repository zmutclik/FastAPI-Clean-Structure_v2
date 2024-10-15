from typing import Annotated, Union, Any, Literal
from enum import Enum
import datetime

from fastapi import APIRouter, Request, Security, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.db.system import engine_db, get_db
from app.schemas import TemplateResponseSet

from app.schemas.__system__.auth import UserSchemas
from app.services.__system__.auth import page_get_current_active_user as get_user_active, get_current_active_user


router = APIRouter(
    prefix="/page/systemsettings",
    tags=["FORM"],
)

templates = Jinja2Templates(directory="templates")
path_template = "pages/system/settings/"


class PathJS(str, Enum):
    indexJs = "index.js"
    formJs = "form.js"
    changeLogJs = "form_changelog.js"


###PAGES###############################################################################################################
from app.repositories.__system__ import SystemRepository, ChangeLogRepository


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def page_system_settings(
    req: Request,
    c_user: Annotated[UserSchemas, Depends(get_user_active)],
    db: Session = Depends(get_db),
):
    return TemplateResponseSet(templates, path_template + "index", req, data={"app": SystemRepository(db).get(),"user": c_user})


@router.get("/{cId}/{sId}/{app_version}/{pathFile}", response_class=HTMLResponse, include_in_schema=False)
def page_js(cId: str, sId: str, req: Request, pathFile: PathJS):
    if req.state.clientId != cId or req.state.sessionId != sId:
        raise HTTPException(status_code=404)
    return TemplateResponseSet(templates, path_template + pathFile, req, cId, sId)


###DATATABLES##########################################################################################################
from app.models.__system__ import ChangeLogTable
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

    query = select(ChangeLogTable, ChangeLogTable.id.label("DT_RowId")).where(ChangeLogTable.deleted_at == None).order_by(ChangeLogTable.id.desc())

    datatable: DataTable = DataTable(
        request_params=params,
        table=query,
        column_names=["DT_RowId", "id", "datetime", "version", "version_name", "description","created_user"],
        engine=engine_db,
        # callbacks=callbacks,
    )
    return datatable.output_result()


###CRUD################################################################################################################
from app.schemas.__system__.settings import SettingsSchemas
from app.schemas.__system__.changelog import changeLogsSchemas, changeLogsSave


@router.post("/{cId}/{sId}", response_model=SettingsSchemas, status_code=202, include_in_schema=False)
async def update(
    dataIn: SettingsSchemas,
    cId: str,
    sId: str,
    req: Request,
    current_user: Annotated[UserSchemas, Security(get_current_active_user, scopes=["admin"])],
    db: Session = Depends(get_db),
):
    if req.state.clientId != cId or req.state.sessionId != sId:
        raise HTTPException(status_code=404)

    repo = SystemRepository(db)
    data = repo.get()
    if data is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")

    return repo.update(dataIn.model_dump())


@router.post("/{cId}/{sId}/changelog", response_model=changeLogsSchemas, status_code=202, include_in_schema=False)
async def changelog_create(
    dataIn: changeLogsSchemas,
    cId: str,
    sId: str,
    req: Request,
    current_user: Annotated[UserSchemas, Security(get_current_active_user, scopes=["admin"])],
    db: Session = Depends(get_db),
):
    if req.state.clientId != cId or req.state.sessionId != sId:
        raise HTTPException(status_code=404)

    repo = ChangeLogRepository(db)

    datas = changeLogsSave.model_validate(dataIn.model_dump())
    datas.created_user = current_user.username

    return repo.create(datas.model_dump())


@router.delete("/{cId}/{sId}/{idCl}", status_code=202, include_in_schema=False)
async def delete(
    idCl: int,
    cId: str,
    sId: str,
    req: Request,
    current_user: Annotated[UserSchemas, Security(get_current_active_user, scopes=["admin"])],
    db: Session = Depends(get_db),
):
    if req.state.clientId != cId or req.state.sessionId != sId:
        raise HTTPException(status_code=404)

    repo = ChangeLogRepository(db)
    data = repo.get(idCl)
    if data is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")

    repo.delete(current_user.username, idCl)
