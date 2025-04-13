from fastapi import APIRouter

from app_name.routes.auth.user import user_router

router = APIRouter()


router.include_router(user_router())
