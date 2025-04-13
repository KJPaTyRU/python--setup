from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from loguru import logger

from app_name.config import get_settings
from app_name.core.middleware import catch_db_excetptions_middleware
from app_name.core.swagger.swagger import (
    add_custom_swagger,
    init_swagger_routes,
)
from app_name.routes import router as main_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    import time

    time.tzset()
    logger.info(
        "[Server] Inited at `http://localhost:{}`", get_settings().app.port
    )
    yield
    logger.info("[Server] Stopped")


def main_sub_app():
    settings = get_settings()
    app = FastAPI(
        debug=settings.app.isDebug,
        title=settings.app.app_name,
        version=settings.app.version,
        docs_url=None,
        redoc_url=None,
    )
    app.include_router(main_router)
    app.middleware("http")(catch_db_excetptions_middleware)

    return app


def create_app():
    settings = get_settings()
    app = FastAPI(
        debug=settings.app.isDebug,
        title=settings.app.app_name,
        version=settings.app.version,
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
    )
    prefix = "/api/app_name/v1"
    sub_app = main_sub_app()

    if settings.app.show_swagger:
        init_swagger_routes(app, "/api/app_name/v0/secret-cdn")
        add_custom_swagger(
            sub_app,
            "",
            openapi_prefix=prefix,
            cdn_prefix="/api/app_name/v0/secret-cdn",
            swagger_ui_parameters={"docExpansion": "none"},
        )

        @app.get("/", include_in_schema=False)
        async def docs_redirect():
            return RedirectResponse(prefix + "/docs")

    app.middleware("http")(catch_db_excetptions_middleware)
    app.mount(prefix, sub_app)

    return app
