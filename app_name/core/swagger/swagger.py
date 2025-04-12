from pathlib import Path
from typing import Any
from fastapi import APIRouter, FastAPI

from fastapi.openapi.docs import get_swagger_ui_oauth2_redirect_html
from fastapi.responses import FileResponse

from app_name.core.swagger.ui import custom_get_swagger_ui_html


def init_swagger_routes(app: FastAPI, prefix="/api/py/secret-cdn"):
    route = APIRouter(prefix=prefix, include_in_schema=False)

    @route.get("/swagger.js")
    def get_js():
        path = Path(__file__).parent / "swagger-ui-bundle.js"
        return FileResponse(path)

    @route.get("/swagger.css")
    def get_css():
        path = Path(__file__).parent / "swagger-ui.css"
        return FileResponse(path)

    app.include_router(route)


def add_custom_swagger(
    app: FastAPI,
    docs_prefix: str,
    openapi_prefix: str | None = None,
    oauth_prefix: str | None = None,
    cdn_prefix="/api/py/secret-cdn",
    swagger_ui_parameters: dict | None = None,
):
    if openapi_prefix is None:
        openapi_prefix = docs_prefix
    if oauth_prefix is None:
        oauth_prefix = docs_prefix

    @app.get(docs_prefix + "/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return custom_get_swagger_ui_html(
            openapi_url=openapi_prefix + "/openapi.json",
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url=f"{cdn_prefix}/swagger.js",
            swagger_css_url=f"{cdn_prefix}/swagger.css",
            swagger_ui_parameters=swagger_ui_parameters,
        )

    @app.get(openapi_prefix + "/openapi.json", include_in_schema=False)
    async def custom_swagger_openapi() -> dict[str, Any]:
        return app.openapi()

    @app.get(
        oauth_prefix + (app.swagger_ui_oauth2_redirect_url or ""),
        include_in_schema=False,
    )
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()

    return app
