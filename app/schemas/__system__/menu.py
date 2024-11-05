from typing import Generic, TypeVar, List, Optional, Union, Annotated, Any, Dict
from pydantic import BaseModel, Json, Field, EmailStr
from datetime import date, time, datetime


class MenuSave(BaseModel):
    text: str
    tooltip: Optional[str] = None
    href: str
    icon: str
    disabled: bool
    menutype_id: Optional[int] = None
    sort: Optional[int] = None


class Menu(BaseModel):
    id: str = Field(coerce_numbers_to_str=True)
    text: str
    tooltip: Optional[str] = None
    href: str
    icon: str
    disabled: Optional[bool] = None


class MenusChild_4(Menu):
    children: Union[List, None] = None


class MenusChild_3(Menu):
    children: Union[List[MenusChild_4], None] = None


class MenusChild_2(Menu):
    children: Union[List[MenusChild_3], None] = None


class MenusChild_1(Menu):
    children: Union[List[MenusChild_2], None] = None


class Menus(Menu):
    children: Union[List[MenusChild_1], None] = None


class MenuTipe(BaseModel):
    id: int
    menutype: str
    desc: str


class MenuTipeSave(BaseModel):
    menutype: str
    desc: str
