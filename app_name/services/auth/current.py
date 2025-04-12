from functools import cache

from sqlalchemy.ext.asyncio import AsyncSession

from app_name.config import get_settings
from app_name.core.crypto.passwords.base import PwdContext
from app_name.core.exceptions import BadTokenError
from app_name.cruds.auth.user import get_user_crud
from app_name.models.auth.user import User
from app_name.schemas.auth.user import UserCreate, UserRawCreate, UserSession
from app_name.services.auth.base import AlchemyTokenAuthService
from app_name.services.auth.jwt.base import create_expires_map
from app_name.services.auth.jwt.sqlalch import AlchemyJwtAuthLogic


@cache
def auth_service() -> AlchemyTokenAuthService:
    settings = get_settings()
    return AlchemyTokenAuthService(
        AlchemyJwtAuthLogic(
            iss=settings.app.app_name,
            aud=settings.app.app_name,
            secret=settings.app.secret,
            expires_map=create_expires_map(
                settings.auth.jwt_access_dt, settings.auth.jwt_refresh_dt
            ),
        )
    )


async def create_user(session: AsyncSession, data: UserRawCreate) -> User:
    obj_in = UserCreate(
        password_hash=PwdContext.hash(data.password),
        **data.model_dump(exclude={"password"}),
    )
    return await get_user_crud().create(session, obj_in)


async def get_active_user(session: AsyncSession, token: str) -> UserSession:
    user = await auth_service().auth(session, token)
    if not user.user.is_active:
        raise BadTokenError()
    return user


async def get_active_superuser(
    session: AsyncSession, token: str
) -> UserSession:
    user = await get_active_user(session, token)
    if not user.user.is_admin:
        raise BadTokenError()
    return user
