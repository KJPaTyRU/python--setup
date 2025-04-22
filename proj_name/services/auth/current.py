from functools import cache
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from proj_name.config import get_settings
from proj_name.core.crypto.passwords.base import PwdContext
from proj_name.core.db.postgres.base import db_session
from proj_name.core.exceptions import BadTokenError
from proj_name.cruds.auth.user import get_user_crud
from proj_name.models.auth.user import User
from proj_name.schemas.auth.user import UserCreate, UserRawCreate, UserSession
from proj_name.services.auth.base import AlchemyTokenAuthService
from proj_name.services.auth.jwt.base import create_expires_map
from proj_name.services.auth.jwt.sqlalch import AlchemyJwtAuthLogic


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


# FastApi #
BeareAuth = OAuth2PasswordBearer(
    tokenUrl=get_settings().app.uri_auth_prefix,
    description="Beare (JWT) Auth",
    auto_error=False,
)
BeareAuthCreds = Annotated[str | None, Depends(BeareAuth)]


async def get_active_user_dep(
    token: BeareAuthCreds, session: AsyncSession = Depends(db_session)
) -> UserSession:
    if token is None:
        logger.debug("[Auth] Got incorrect Authorization header: {}", token)
        raise BadTokenError()
    return await get_active_user(session, token)


async def get_active_superuser_dep(
    token: BeareAuthCreds, session: AsyncSession = Depends(db_session)
) -> UserSession:
    if token is None:
        logger.debug("[Auth] Got incorrect Authorization header: {}", token)
        raise BadTokenError()
    return await get_active_superuser(session, token)
