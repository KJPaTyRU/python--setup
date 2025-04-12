from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger

from app_name.config import get_settings
from app_name.core.exceptions import AppException

_ERROR_FUNC = get_settings().logger_error_func
_INFO_FUNC = get_settings().logger_info_func


async def catch_db_excetptions_middleware(
    request: Request, call_next
) -> Response:
    """middleware for catching some exceptions in db inserts"""
    try:
        resp: Response = await call_next(request)
        logger.info(
            '"{} {}" {}', request.method, request.url, resp.status_code
        )
        return resp

    except AppException as e:
        _INFO_FUNC("{} | {} | {}", e.__class__.__name__, e.status, e.code)
        logger.debug(
            f"{e.__class__.__name__} | {e.status} |"
            f" {dict(request.headers.items())}"
        )
        return JSONResponse(jsonable_encoder(e.details), status_code=e.status)
    except BaseException:
        _ERROR_FUNC("SWW")
        e = AppException()
        return JSONResponse(jsonable_encoder(e.details), status_code=e.status)
