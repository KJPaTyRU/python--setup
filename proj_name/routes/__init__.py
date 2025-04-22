from fastapi import APIRouter

from proj_name.routes.default import default_router
from proj_name.routes.auth import router as auth_router

router = APIRouter()


router.include_router(auth_router)
router.include_router(default_router())
