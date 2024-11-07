from sqlalchemy.orm import Session
from app.core.db.auth import engine_db
from app.core.db.system import engine_db as engine_db_sys
from app.repositories.__system__.auth import GroupsRepository, UsersRepository
from app.repositories.__system__ import MenuRepository

from app.schemas.__system__.menu import Menus

text = """<li class="nav-item has-treeview {}">
    <a href="{}" class="nav-link {}">
    <i class="nav-icon {}"></i>
    <p>{}{}</p>
    </a>"""


def menu_to_text(menus, segmen: str, parent_id=0):
    resText = """<ul class="nav nav-treeview">"""
    if parent_id == 0:
        resText = """<ul class="nav nav-pills nav-sidebar flex-column" data-widget="treeview" role="menu" data-accordion="false">"""
    for item in menus:
        menu_open = "menu-open" if item["segment"] in segmen else ""
        menu_active = "active" if item["segment"] in segmen else ""
        if len(item["children"]) > 0:
            resText = resText + text.format(
                menu_open,
                item["href"],
                menu_active,
                item["icon"],
                item["text"],
                '<i class="right fas fa-angle-left"></i>',
            )
            resText = resText + menu_to_text(item["children"], segmen, item["parent_id"])
        else:
            resText = resText + text.format(
                menu_open,
                item["href"],
                menu_active,
                item["icon"],
                item["text"],
                "",
            )
        resText = resText + "</li>"
    resText = resText + "</ul>"
    return resText


def get_menus(menutype_id: int, user_id: int, segmen: str):
    with engine_db.begin() as connection:
        with Session(bind=connection) as db:
            with engine_db_sys.begin() as connection_sys:
                with Session(bind=connection_sys) as db_sys:
                    repo_u = UsersRepository(db)
                    repo_g = GroupsRepository(db)
                    repo_m = MenuRepository(db_sys)

                    list_idMenu = []
                    lgroup = repo_u.list_group(user_id)
                    for item in lgroup:
                        dt = repo_g.list_menu(menutype_id, item)
                        for it in dt:
                            list_idMenu.append(it)

                    list_idMenu = list(dict.fromkeys(list_idMenu))
                    parent_id = repo_m.list_parent(list_idMenu)
                    list_idMenu = list_idMenu + parent_id
                    list_idMenu = list(dict.fromkeys(list_idMenu))

                    menus = repo_m.get_0(menutype_id, 0, list_idMenu)

                    return menu_to_text(menus, segmen)
