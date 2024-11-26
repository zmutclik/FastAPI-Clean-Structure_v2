from typing import Annotated, Any, List
from enum import Enum

from fastapi import APIRouter, Security, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.db.auth import engine_db, get_db
from app.schemas import PageResponseSchemas

from app.schemas.__system__.auth import UserSchemas
from app.services.__system__.auth import get_active_user
from app.repositories.__system__ import MenuRepository
from app.core.db.system import get_db as get_db_sys


router = APIRouter(
    prefix="/sys/groups",
    tags=["FORM"],
)

pageResponse = PageResponseSchemas("templates", "pages/system/groups/", router.prefix)
db: Session = Depends(get_db)
db_sys: Session = Depends(get_db_sys)
req_page = Annotated[PageResponseSchemas, Depends(pageResponse.page)]
req_depends = Annotated[PageResponseSchemas, Depends(pageResponse.pageDepends)]
req_nonAuth = Annotated[PageResponseSchemas, Depends(pageResponse.pageDependsNonUser)]
c_user_scope = Annotated[UserSchemas, Security(get_active_user, scopes=["admin", "pages"])]


class PathJS(str, Enum):
    indexJs = "index.js"
    formJs = "form.js"


###PAGES###############################################################################################################
from app.repositories.__system__.auth import GroupsRepository


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def page_system_akun_groups(req: req_page):
    return pageResponse.response("index.html")


@router.get("/{cId}/{sId}/menu/{menutype_id:int}/{id_group:int}", status_code=200, include_in_schema=False)
def data_menus(id_group: int, menutype_id: int, db_sys=db_sys, db=db):
    data = MenuRepository(db_sys).all(menutype_id)
    listmenu = GroupsRepository(db).list_menu(menutype_id, id_group)
    res = []
    for item in data:
        dt = {
            "id": str(item.id),
            "text": item.text,
            "icon": item.icon,
            "parent": "#" if item.parent_id == 0 else str(item.parent_id),
            "state": {"opened": True, "disabled": item.disabled, "selected": True if item.id in listmenu else False},
        }
        res.append(dt)
    return res


@router.get("/{cId}/{sId}/add", response_class=HTMLResponse, include_in_schema=False)
def page_system_groups_add(req: req_page, db_sys=db_sys):
    pageResponse.addData("menutype", MenuRepository(db_sys).allType())
    return pageResponse.response("form.html")


@router.get("/{cId}/{sId}/{id:int}", response_class=HTMLResponse, include_in_schema=False)
def page_system_groups_form(id: int, req: req_page, db_sys=db_sys, db=db):
    pageResponse.addData("group", GroupsRepository(db).getById(id))
    pageResponse.addData("menutype", MenuRepository(db_sys).allType())
    return pageResponse.response("form.html")


@router.get("/{cId}/{sId}/{app_version}/{pathFile}", response_class=HTMLResponse, include_in_schema=False)
def page_js(req: req_nonAuth, pathFile: PathJS, group: int = 0):
    req.state.islogsave = False
    pageResponse.addData("group", group)
    return pageResponse.response(pathFile)


###DATATABLES##########################################################################################################
from app.models.__system__ import GroupsTable
from sqlalchemy import select
from datatables import DataTable


@router.post("/{cId}/{sId}/datatables", status_code=202, include_in_schema=False)
def get_datatables(params: dict[str, Any], req: req_depends, c_user: c_user_scope) -> dict[str, Any]:
    query = select(GroupsTable, GroupsTable.id.label("DT_RowId"))

    datatable: DataTable = DataTable(
        request_params=params,
        table=query,
        column_names=["DT_RowId", "id", "group", "desc"],
        engine=engine_db,
        # callbacks=callbacks,
    )
    return datatable.output_result()


###CRUD################################################################################################################
from app.schemas.__system__.auth.group import Groups, GroupSave, GroupIn


@router.post("/{cId}/{sId}", response_model=Groups, status_code=201, include_in_schema=False)
async def create(dataIn: GroupIn, req: req_depends, c_user: c_user_scope, db_sys=db_sys, db=db):
    repo = GroupsRepository(db)
    if repo.get(dataIn.group):
        raise HTTPException(status_code=400, detail="Grup sudah ada yang menggunakan.")
    dt = GroupSave.model_validate(dataIn.model_dump())
    data = repo.create(dt.model_dump())
    repo.save_menu(data.id, dataIn.menutype_id, dataIn.menu)
    return data


@router.post("/{cId}/{sId}/{id:int}", response_model=Groups, status_code=202, include_in_schema=False)
async def update(dataIn: GroupIn, id: int, req: req_depends, c_user: c_user_scope, db_sys=db_sys, db=db):
    repo = GroupsRepository(db)
    data = repo.getById(id)
    if data is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")

    dt = GroupSave.model_validate(dataIn.model_dump())
    data = repo.update(id, dt.model_dump())
    repo.empty_menu(id, dataIn.menutype_id)
    repo.save_menu(data.id, dataIn.menutype_id, dataIn.menu)
    return data


@router.delete("/{cId}/{sId}/{id:int}", status_code=202, include_in_schema=False)
async def delete(id: int, req: req_depends, c_user: c_user_scope, db=db):
    repo = GroupsRepository(db)
    data = repo.getById(id)
    if data is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")

    return repo.delete(id)


###MENU################################################################################################################
