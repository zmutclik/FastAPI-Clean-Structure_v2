from fastapi import APIRouter, Request
from starlette.responses import FileResponse

router = APIRouter()


@router.get("/", include_in_schema=False)
async def root(request: Request):
    return {"message": "Hello BOZ " + request.client.host + " !!!"}


@router.get("/favicon.ico", include_in_schema=False)
def favicon(request: Request):
    request.state.issave = False
    return FileResponse("files/static/favicon.ico")
