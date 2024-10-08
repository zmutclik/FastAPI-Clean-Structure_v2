from fastapi import APIRouter, Request
from starlette.responses import FileResponse

router = APIRouter()


@router.get("/")
async def root(request: Request):
    return {"message": "Hello BOZ " + request.client.host + " !!!"}


@router.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse("files/static/favicon.ico")
