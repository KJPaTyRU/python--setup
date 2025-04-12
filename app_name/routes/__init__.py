from fastapi import APIRouter

from app_name.routes.default import default_router

router = APIRouter()


router.include_router(default_router())
