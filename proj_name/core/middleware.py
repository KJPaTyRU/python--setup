from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError

from proj_name.config import get_settings
from proj_name.core.exceptions import AppException, AuthException

_ERROR_FUNC = get_settings().logger_error_func
_INFO_FUNC = get_settings().logger_info_func


def add_catch_excpetion_middlware(app: FastAPI):
    @app.exception_handler(ValidationError)
    async def handelr_ValidationError(request: Request, e: ValidationError):
        try:
            body = await request.body()
        except Exception:
            body = b""
        logger.debug(
            f"{e.__class__.__name__} | 422 |"
            f" {dict(request.headers.items())} | {body}"
        )
        return JSONResponse(jsonable_encoder(e.errors()), status_code=422)

    @app.exception_handler(AuthException)
    async def handelr_AuthException(request: Request, e: AuthException):
        return JSONResponse(jsonable_encoder(e.details), status_code=e.status)

    @app.exception_handler(AppException)
    async def handelr_AppException(request: Request, e: AppException):
        _INFO_FUNC("{} | {} | {}", e.__class__.__name__, e.status, e.code)
        try:
            body = await request.body()
        except Exception:
            body = b""
        logger.debug(
            f"{e.__class__.__name__} | {e.status} |"
            f" {dict(request.headers.items())} | {body}"
        )
        return JSONResponse(jsonable_encoder(e.details), status_code=e.status)

    @app.exception_handler(Exception)
    async def handelr_Exception(request: Request, e: Exception):
        _ERROR_FUNC("SWW")
        e = AppException()
        return JSONResponse(jsonable_encoder(e.details), status_code=e.status)
