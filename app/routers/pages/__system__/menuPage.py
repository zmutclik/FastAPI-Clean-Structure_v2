from typing import Annotated, Any, List
from enum import Enum

from fastapi import APIRouter, Security, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.db.system import engine_db, get_db
from app.schemas import PageResponseSchemas

from app.schemas.__system__.auth import UserSchemas
from app.services.__system__.auth import get_active_user


router = APIRouter(
    prefix="/menu",
    tags=["FORM"],
)

pageResponse = PageResponseSchemas("templates", "pages/system/menu/")
db: Session = Depends(get_db)
req_page = Annotated[PageResponseSchemas, Depends(pageResponse.page)]
req_depends = Annotated[PageResponseSchemas, Depends(pageResponse.pageDepends)]
req_nonAuth = Annotated[PageResponseSchemas, Depends(pageResponse.pageDependsNonUser)]
c_user_scope = Annotated[UserSchemas, Security(get_active_user, scopes=["admin", "pages"])]


class PathJS(str, Enum):
    indexJs = "index.js"
    formJs = "form.js"
    detailJs = "detail.js"


###PAGES###############################################################################################################
from app.repositories.__system__ import MenuRepository


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def page_system_menu(req: req_page):
    return pageResponse.response("index.html")


@router.get("/detail/{cId}/{sId}/{menutype_id:int}", response_class=HTMLResponse, include_in_schema=False)
def page_system_menu_form_detail(menutype_id: int, req: req_page, db=db):
    pageResponse.addData("menutype", MenuRepository(db).getTypeID(menutype_id))
    return pageResponse.response("detail.html")


@router.get("/{cId}/{sId}/add", response_class=HTMLResponse, include_in_schema=False)
def page_system_menu_add(req: req_page):
    return pageResponse.response("form.html")


@router.get("/{cId}/{sId}/{id:int}", response_class=HTMLResponse, include_in_schema=False)
def page_system_menu_form(id: int, req: req_page, db=db):
    pageResponse.addData("menutype", MenuRepository(db).getTypeID(id))
    return pageResponse.response("form.html")


@router.get("/{cId}/{sId}/{app_version}/{pathFile}", response_class=HTMLResponse, include_in_schema=False)
def page_js(req: req_nonAuth, pathFile: PathJS):
    req.state.islogsave = False
    return pageResponse.response(pathFile)


###DATATABLES##########################################################################################################
from app.models.__system__ import MenuTypeTable, MenuTable
from sqlalchemy import select
from datatables import DataTable


@router.post("/{cId}/{sId}/datatables", status_code=202, include_in_schema=False)
def get_datatables(params: dict[str, Any], req: req_depends, c_user: c_user_scope) -> dict[str, Any]:
    query = select(MenuTypeTable, MenuTypeTable.id.label("DT_RowId"))

    datatable: DataTable = DataTable(
        request_params=params,
        table=query,
        column_names=["DT_RowId", "id", "menutype", "desc"],
        engine=engine_db,
        # callbacks=callbacks,
    )
    return datatable.output_result()


###CRUD################################################################################################################
from app.schemas.__system__.menu import MenuTipe, MenuTipeSave


@router.post("/{cId}/{sId}", response_model=MenuTipe, status_code=201, include_in_schema=False)
def create(dataIn: MenuTipeSave, req: req_depends, c_user: c_user_scope, db=db):
    repo = MenuRepository(db)
    if repo.getType(dataIn.menutype):
        raise HTTPException(status_code=400, detail="MenuType sudah ada yang menggunakan.")

    return repo.createType(dataIn.model_dump())


@router.post("/{cId}/{sId}/{id:int}", response_model=MenuTipe, status_code=202, include_in_schema=False)
def update(dataIn: MenuTipeSave, id: int, req: req_depends, c_user: c_user_scope, db=db):
    repo = MenuRepository(db)
    data = repo.getTypeID(id)
    if data is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")

    return repo.updateType(id, dataIn.model_dump())


@router.delete("/{cId}/{sId}/{id:int}", status_code=202, include_in_schema=False)
def delete(id: int, req: req_depends, c_user: c_user_scope, db=db):
    repo = MenuRepository(db)
    data = repo.getTypeID(id)
    if data is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")

    return repo.deleteType(id)


###CRUD################################################################################################################
from app.schemas.__system__.menu import Menus, Menu, MenuSave


@router.get("/detail/{cId}/{sId}/{menutype_id:int}/menus", response_model=List[Menus], status_code=200, include_in_schema=False)
def data_menus(menutype_id: int, req: req_depends, c_user: c_user_scope, db=db):
    return MenuRepository(db).get_0(menutype_id)


@router.get("/detail/{cId}/{sId}/{menutype_id:int}/data/{id:int}", response_model=Menus, status_code=200, include_in_schema=False)
def data_menu(id: int, menutype_id: int, req: req_depends, c_user: c_user_scope, db=db):
    data = MenuRepository(db).get(id)
    if data.menutype_id != str(menutype_id):
        raise HTTPException(status_code=404, detail="Data tidak cocok.")
    return data


def menu_sorting_save(repo, parent_id: int, dataIn: List[dict]):
    i = 0
    for item in dataIn:
        i = i + 1
        repo.update(int(item.id), {"parent_id": parent_id, "sort": i})
        if len(item.children) > 0:
            menu_sorting_save(repo, item.id, item.children)


@router.post("/detail/{cId}/{sId}/{menutype_id:int}/menus", status_code=201, include_in_schema=False)
def menu_sorting(dataIn: List[Menus], menutype_id: int, req: req_depends, c_user: c_user_scope, db=db):
    repo = MenuRepository(db)
    menu_sorting_save(repo, 0, dataIn)


@router.post("/detail/{cId}/{sId}/{menutype_id:int}/data", response_model=Menu, status_code=201, include_in_schema=False)
def menu_create(dataIn: MenuSave, menutype_id: int, req: req_depends, c_user: c_user_scope, db=db):
    repo = MenuRepository(db)
    dataIn.menutype_id = menutype_id
    dataIn.sort = repo.getTypeCount(menutype_id) + 1
    return repo.create(dataIn.model_dump())


@router.post("/detail/{cId}/{sId}/{menutype_id:int}/data/{id:int}", response_model=Menu, status_code=202, include_in_schema=False)
def menu_update(dataIn: MenuSave, id: int, menutype_id: int, req: req_depends, c_user: c_user_scope, db=db):
    repo = MenuRepository(db)
    data = repo.get(id)
    if data is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")
    if data.menutype_id != str(menutype_id):
        raise HTTPException(status_code=404, detail="Data tidak cocok.")

    dataIn.menutype_id = menutype_id
    return repo.update(id, dataIn.model_dump())


@router.delete("/detail/{cId}/{sId}/{menutype_id:int}/data/{id:int}", status_code=202, include_in_schema=False)
def menu_delete(id: int, menutype_id: int, req: req_depends, c_user: c_user_scope, db=db):
    repo = MenuRepository(db)
    data = repo.get(id)
    if data is None:
        raise HTTPException(status_code=400, detail="Data Tida ada.")
    if data.menutype_id != str(menutype_id):
        raise HTTPException(status_code=404, detail="Data tidak cocok.")

    return repo.delete(id)
