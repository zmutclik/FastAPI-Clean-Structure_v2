from typing import Generic, TypeVar, List, Optional, Union, Annotated, Any, Dict
from pydantic import BaseModel, Json, Field, EmailStr
from datetime import date, time, datetime
from fastapi import Request, HTTPException
from app.core import config


def TemplateResponseSet(
    templates: Any,
    path_template: str,
    request: Request,
    clientId: Union[str, None] = None,
    sessionId: Union[str, None] = None,
    media_type: str = "text/html",
    data: dict = {},
):
    if clientId is not None or sessionId is not None:
        if request.state.clientId != clientId or request.state.sessionId != sessionId:
            raise HTTPException(status_code=404)

    if path_template.find(".js") > 0:
        media_type = "application/javascript"
    else:
        path_template = path_template + ".html"

    context = {
        "app_name": config.APP_NAME,
        "app_version": config.APP_VERSION,
        "clientId": request.state.clientId,
        "sessionId": request.state.sessionId,
        "TOKEN_KEY": config.TOKEN_KEY,
        "segment": request.scope["route"].name,
    }

    context.update(data)
    return templates.TemplateResponse(
        request=request,
        name=path_template,
        media_type=media_type,
        context=context,
    )
