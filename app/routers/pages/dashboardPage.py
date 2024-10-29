from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from app.schemas import PageResponseSchemas

router = APIRouter(
    prefix="",
    tags=["FORM"],
)
pageResponse = PageResponseSchemas("templates", "pages/dashboard/")
req_page = Annotated[PageResponseSchemas, Depends(pageResponse.page)]


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def dashboard(req: req_page):
    return pageResponse.response("index2.html")
