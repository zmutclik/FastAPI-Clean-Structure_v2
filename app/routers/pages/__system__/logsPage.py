from typing import Annotated, Union, Any, Literal
from enum import Enum
import datetime

from fastapi import APIRouter, Request, Security, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.db.logs import get_db
from app.schemas import TemplateResponseSet

from app.schemas.__system__.auth import UserSchemas
from app.services.__system__.auth import page_get_current_active_user as get_user_active, get_current_active_user


router = APIRouter(
    prefix="/page/logs",
    tags=["FORM"],
)

templates = Jinja2Templates(directory="templates")
path_template = "pages/system/logs/"


class PathJS(str, Enum):
    indexJs = "index.js"


###PAGES###############################################################################################################
from app.repositories.__system__ import LogsRepository


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def page_system_logs(
    req: Request,
    c_user: Annotated[UserSchemas, Depends(get_user_active)],
):
    repo = LogsRepository(datetime.datetime.now())
    return TemplateResponseSet(
        templates,
        path_template + "index",
        req,
        data={"ip": repo.getIPs(),"user": c_user},
    )


@router.get("/{cId}/{sId}/{app_version}/{pathFile}", response_class=HTMLResponse, include_in_schema=False)
def page_js(cId: str, sId: str, req: Request, pathFile: PathJS):
    if req.state.clientId != cId or req.state.sessionId != sId:
        raise HTTPException(status_code=404)
    return TemplateResponseSet(templates, path_template + pathFile, req, cId, sId)


###DATATABLES##########################################################################################################
from app.models.__system__ import TableLogs
from sqlalchemy import select, create_engine
from datatables import DataTable


@router.post("/{cId}/{sId}/datatables", status_code=202, include_in_schema=False)
def get_datatables(
    params: dict[str, Any],
    cId: str,
    sId: str,
    request: Request,
    current_user: Annotated[UserSchemas, Security(get_current_active_user, scopes=["admin"])],
) -> dict[str, Any]:
    if request.state.clientId != cId or request.state.sessionId != sId:
        raise HTTPException(status_code=404)

    print(params["search"]["time_start"])
    tahunbulan = datetime.datetime.strptime(params["search"]["time_start"], "%Y-%m-%d %H:%M:%S")
    fileDB_ENGINE = "./files/database/db/logs_{}.db".format(tahunbulan.strftime("%Y-%m"))
    DB_ENGINE = "sqlite:///" + fileDB_ENGINE
    engine_db = create_engine(DB_ENGINE, connect_args={"check_same_thread": False})


    query = select(TableLogs, TableLogs.id.label("DT_RowId")).filter(
        TableLogs.startTime >= params["search"]["time_start"],
        TableLogs.startTime <= params["search"]["time_end"],
    )

    if params["search"]["ipaddress"] != "":
        query = query.filter(TableLogs.ipaddress.like("%" + params["search"]["ipaddress"] + "%"))

    if params["search"]["method"] != "":
        query = query.filter(TableLogs.method == params["search"]["method"])

    if params["search"]["status"] != "":
        query = query.filter(TableLogs.status_code.like(params["search"]["status"] + "%"))

    if params["search"]["path"] != "":
        query = query.filter(TableLogs.path.like("%" + params["search"]["path"] + "%"))

    if params["search"]["params"] != "":
        query = query.filter(TableLogs.path_params.like("%" + params["search"]["params"] + "%"))

    query = query.order_by(TableLogs.id.desc())

    datatable: DataTable = DataTable(
        request_params=params,
        table=query,
        column_names=[
            "DT_RowId",
            "id",
            "client_id",
            "session_id",
            "startTime",
            "app",
            "platform",
            "browser",
            "path",
            "method",
            "ipaddress",
            "username",
            "status_code",
            "process_time",
        ],
        engine=engine_db,
        # callbacks=callbacks,
    )
    return datatable.output_result()
