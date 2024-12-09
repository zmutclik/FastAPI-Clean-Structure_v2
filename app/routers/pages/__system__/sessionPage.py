from typing import Annotated, Any
from enum import Enum

from fastapi import APIRouter, Security, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.db.session import engine_db, get_db
from app.schemas import PageResponseSchemas

from app.schemas.__system__.auth import UserSchemas
from app.services.__system__.auth import get_active_user


router = APIRouter(
    prefix="/sys/session",
    tags=["FORM"],
)

pageResponse = PageResponseSchemas("templates", "pages/system/session/", router.prefix)
db: Session = Depends(get_db)
req_page = Annotated[PageResponseSchemas, Depends(pageResponse.page)]
req_depends = Annotated[PageResponseSchemas, Depends(pageResponse.pageDepends)]
req_nonAuth = Annotated[PageResponseSchemas, Depends(pageResponse.pageDependsNonUser)]
c_user_scope = Annotated[UserSchemas, Security(get_active_user, scopes=["admin", "pages"])]


class PathJS(str, Enum):
    indexJs = "index.js"
    formJs = "form.js"


###PAGES###############################################################################################################
from app.repositories.__system__.auth import SessionRepository


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def page_system_session(req: req_page):
    return pageResponse.response("index.html")


@router.get("/{cId}/{sId}/add", response_class=HTMLResponse, include_in_schema=False)
def page_system_session_add(req: req_page):
    return pageResponse.response("form.html")


@router.get("/{cId}/{sId}/{app_version}/{pathFile}", response_class=HTMLResponse, include_in_schema=False)
def page_js(req: req_nonAuth, pathFile: PathJS):
    req.state.islogsave = False
    return pageResponse.response(pathFile)


###DATATABLES##########################################################################################################
from app.models.__system__ import SessionTable, SessionEndTable
from sqlalchemy import select
from datatables import DataTable


@router.post("/{cId}/{sId}/{status}/datatables", status_code=202, include_in_schema=False)
def get_datatables(params: dict[str, Any], status: str, req: req_depends, c_user: c_user_scope) -> dict[str, Any]:
    query = select(SessionTable, SessionTable.id.label("DT_RowId")).order_by(SessionTable.active.desc(),SessionTable.type.desc(),SessionTable.EndTime.desc())

    datatable: DataTable = DataTable(
        request_params=params,
        table=query,
        column_names=[
            "DT_RowId",
            "id",
            "type",
            "session_id",
            "username",
            "platform",
            "browser",
            "startTime",
            "EndTime",
            "LastPage",
            "ipaddress",
            "active",
        ],
        engine=engine_db,
        # callbacks=callbacks,
    )
    return datatable.output_result()


@router.delete("/{cId}/{sId}/{id:int}", status_code=202, include_in_schema=False)
async def kill_session(id: int, req: req_depends, c_user: c_user_scope, db=db):
    repo = SessionRepository()
    dataS = repo.getById(id)
    if dataS is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")

    repo.update(id, {"active": False})
