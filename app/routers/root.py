from typing import Annotated
from starlette.responses import FileResponse
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from app.schemas import PageResponseSchemas

router = APIRouter()

pageResponse = PageResponseSchemas("templates", "pages/dashboard/")
req_page = Annotated[PageResponseSchemas, Depends(pageResponse.page)]


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard(req: req_page):
    return pageResponse.response("index2.html")


# @router.get("/", include_in_schema=False)
# async def root(request: Request):
#     return {"message": "Hello BOZ " + request.client.host + " !!!"}


@router.get("/favicon.ico", include_in_schema=False)
def favicon(request: Request):
    request.state.islogsave = False
    return FileResponse("files/static/favicon.ico")
