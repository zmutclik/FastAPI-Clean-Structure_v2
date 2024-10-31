from typing import Annotated, Any
from enum import Enum
import datetime

from fastapi import APIRouter, Security, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.db.logs import get_db
from app.schemas import PageResponseSchemas
from app.schemas.__system__.auth import UserSchemas
from app.services.__system__.auth import get_active_user


router = APIRouter(
    prefix="/logs",
    tags=["FORM"],
)

pageResponse = PageResponseSchemas("templates", "pages/system/logs/")
db: Session = Depends(get_db)
req_page = Annotated[PageResponseSchemas, Depends(pageResponse.page)]
req_depends = Annotated[PageResponseSchemas, Depends(pageResponse.pageDepends)]
req_nonUser = Annotated[PageResponseSchemas, Depends(pageResponse.pageDependsNonUser)]
c_user_scope = Annotated[UserSchemas, Security(get_active_user, scopes=["admin", "pages"])]


class PathJS(str, Enum):
    indexJs = "index.js"


###PAGES###############################################################################################################
from app.repositories.__system__ import LogsRepository


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def page_system_logs(req: req_page):
    repo = LogsRepository(datetime.datetime.now())
    pageResponse.addData("ip", repo.getIPs())
    return pageResponse.response("index.html")


@router.get("/{cId}/{sId}/{app_version}/{pathFile}", response_class=HTMLResponse, include_in_schema=False)
def page_js(req: req_nonUser, pathFile: PathJS):
    req.state.islogsave = False
    return pageResponse.response(pathFile)


###DATATABLES##########################################################################################################
from app.models.__system__ import TableLogs
from sqlalchemy import select, create_engine
from datatables import DataTable


@router.post("/{cId}/{sId}/datatables", status_code=202, include_in_schema=False)
def get_datatables(params: dict[str, Any], req: req_depends, c_user: c_user_scope) -> dict[str, Any]:
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
