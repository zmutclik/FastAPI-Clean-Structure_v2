from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from app.schemas import PageResponseSchemas

router = APIRouter(
    prefix="/documentation",
    tags=["FORM"],
)

pageResponse = PageResponseSchemas("templates", "pages/")
req_page = Annotated[None, Depends(pageResponse.page)]


@router.get("", response_class=HTMLResponse, include_in_schema=False)
def documentation_page(req: req_page):
    return pageResponse.response("documentation.html")
