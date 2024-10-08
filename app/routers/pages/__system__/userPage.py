from typing import Annotated, Union, Any, Literal
from enum import Enum

from fastapi import APIRouter, Request, Response, Cookie, Security, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core import config
from app.core.db.auth import engine_db, get_db
from app.schemas.__system__.auth import UserSchemas
from app.services.__system__.auth import page_get_current_active_user as get_user_active
from app.models.__system__ import auth
from app.schemas import TemplateResponseSet
from app.repositories.__system__.auth import UsersRepository

from sqlalchemy import select

from datatables import DataTable

router = APIRouter(
    prefix="/page/users",
    tags=["FORM"],
)
templates = Jinja2Templates(directory="templates")
path_template = "page/system/users/"


class PathJS(str, Enum):
    indexJs = "index.js"
    formJs = "form.js"


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def page_system_users(
    req: Request,
    c_user: Annotated[UserSchemas, Depends(get_user_active)],
):
    return TemplateResponseSet(templates, path_template + "index", req)


@router.get("/{cId}/{sId}/add", response_class=HTMLResponse, include_in_schema=False)
def page_system_users_form(cId: str, sId: str, req: Request, c_user: Annotated[UserSchemas, Depends(get_user_active)]):
    return TemplateResponseSet(templates, path_template + "form", req, cId, sId)


@router.get("/{cId}/{sId}/{id:int}", response_class=HTMLResponse, include_in_schema=False)
def page_system_users_form(
    cId: str,
    sId: str,
    id: int,
    req: Request,
    c_user: Annotated[UserSchemas, Depends(get_user_active)],
    db: Session = Depends(get_db),
):
    return TemplateResponseSet(templates, path_template + "form", req, cId, sId, data={"user": UsersRepository(db).getById(id)})


@router.get("/{cId}/{sId}/{app_version}/{pathFile}", response_class=HTMLResponse, include_in_schema=False)
def page_js(cId: str, sId: str, req: Request, pathFile: PathJS):
    return TemplateResponseSet(templates, path_template + pathFile, req, cId, sId)


@router.post("/{clientId}/{sessionId}/datatables", status_code=201, include_in_schema=False)
def get_datatable_result(
    params: dict[str, Any],
    clientId: str,
    sessionId: str,
    request: Request,
) -> dict[str, Any]:
    if request.state.clientId == clientId and request.state.sessionId == sessionId:
        datatable: DataTable = DataTable(
            request_params=params,
            table=select(auth.UsersTable, auth.UsersTable.id.label("DT_RowId")),
            column_names=["DT_RowId", "id", "username", "email", "full_name"],
            engine=engine_db,
            # callbacks=callbacks,
        )
        return datatable.output_result()
    else:
        raise HTTPException(status_code=404)
