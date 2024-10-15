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
from app.services.__system__.auth import (
    page_get_current_active_user as get_user_active,
    get_current_active_user,
)


router = APIRouter(
    prefix="/page/repository",
    tags=["FORM"],
)

templates = Jinja2Templates(directory="templates")
path_template = "pages/system/repository/"


class PathJS(str, Enum):
    indexJs = "index.js"
    formJs = "form.js"


###PAGES###############################################################################################################
from app.repositories.__system__.repository import Repository


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def page_system_repository(
    req: Request,
    c_user: Annotated[UserSchemas, Depends(get_user_active)],
):
    return TemplateResponseSet(
        templates,
        path_template + "index",
        req,
        data={"user": c_user},
    )


@router.get("/{cId}/{sId}/add", response_class=HTMLResponse, include_in_schema=False)
def page_system_repository_add(
    cId: str,
    sId: str,
    req: Request,
    c_user: Annotated[UserSchemas, Depends(get_user_active)],
):
    if req.state.clientId != cId or req.state.sessionId != sId:
        raise HTTPException(status_code=404)
    return TemplateResponseSet(
        templates,
        path_template + "form",
        req,
        cId,
        sId,
        data={"user": c_user},
    )


@router.get(
    "/{cId}/{sId}/{id:int}", response_class=HTMLResponse, include_in_schema=False
)
def page_system_repository_form(
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
        data={"repository": Repository(db).get(id), "user": c_user},
    )


@router.get(
    "/{cId}/{sId}/{app_version}/{pathFile}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def page_js(cId: str, sId: str, req: Request, pathFile: PathJS):
    if req.state.clientId != cId or req.state.sessionId != sId:
        raise HTTPException(status_code=404)
    return TemplateResponseSet(templates, path_template + pathFile, req, cId, sId)


###DATATABLES##########################################################################################################
from app.models.__system__ import RepositoryTable
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

    query = select(RepositoryTable, RepositoryTable.id.label("DT_RowId")).filter(
        RepositoryTable.deleted_at == None,
    )

    datatable: DataTable = DataTable(
        request_params=params,
        table=query,
        column_names=[
            "DT_RowId",
            "id",
            "name",
            "type",
            "value",
            "active",
        ],
        engine=engine_db,
        # callbacks=callbacks,
    )
    return datatable.output_result()


###CRUD################################################################################################################
from app.schemas.__system__.repository import (
    RepositorysSchemas,
    RepositorySave,
    RepositoryData,
)


@router.post(
    "/{cId}/{sId}",
    response_model=RepositorysSchemas,
    status_code=201,
    include_in_schema=False,
)
async def create(
    dataIn: RepositoryData,
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

    repo = Repository(db)
    data = RepositorySave.model_validate(dataIn.model_dump())
    data.created_user = current_user.username
    cdata = repo.create(data.model_dump())

    return cdata


@router.post(
    "/{cId}/{sId}/{idS}",
    response_model=RepositorysSchemas,
    status_code=202,
    include_in_schema=False,
)
async def update(
    dataIn: RepositoryData,
    idR: int,
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

    repo = Repository(db)
    data = repo.get(idR)
    if data is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")

    return repo.update(idR, dataIn.model_dump())


@router.delete("/{cId}/{sId}/{idR}", status_code=202, include_in_schema=False)
async def delete(
    idR: int,
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

    repo = Repository(db)
    data = repo.get(idR)
    if data is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")

    return repo.delete(current_user.username, idR)
