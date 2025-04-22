from typing import Annotated
from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from proj_name.config import get_settings
from proj_name.core.crypto.passwords.base import PwdContext
from proj_name.core.db.postgres.base import db_session
from proj_name.core.fastapi.filter.depends import FilterDepends
from proj_name.core.fastapi.ordering.current import OrderingDepends
from proj_name.core.fastapi.ordering.sqlalchemy import AlchOrderConsturctor
from proj_name.core.fastapi.pagination.sqlalchemy import (
    AlchemyBasePaginator,
    paginator1000,
)
from proj_name.core.fastapi.routes.utils import get_uuid_ids_query, model_get
from proj_name.cruds.auth.user import UserCrud, get_user_crud
from proj_name.filters.auth.user import UserFilter
from proj_name.schemas.auth.token import RefreshToken, TokenPair
from proj_name.schemas.auth.types import UserNameStr
from proj_name.schemas.auth.user import (
    UserCreate,
    UserFullRead,
    UserLogin,
    UserMeUpdate,
    UserRawCreate,
    UserRegister,
    UserSession,
    UserUpdate,
)
from proj_name.services.auth.base import AlchemyTokenAuthService
from proj_name.services.auth.current import (
    auth_service,
    get_active_superuser_dep,
    get_active_user_dep,
)

router = APIRouter(prefix="", tags=["User & Auth"])


def user_router() -> APIRouter:
    return router


@router.get("/users")
async def get_users(
    response: Response,
    user: UserSession = Depends(get_active_superuser_dep),
    session: AsyncSession = Depends(db_session),
    crud: UserCrud = Depends(get_user_crud),
    paginator: AlchemyBasePaginator = Depends(paginator1000),
    ordering: AlchOrderConsturctor = OrderingDepends(
        get_user_crud().get_ordering_meta()
    ),
    filter_schema: UserFilter = FilterDepends(UserFilter),
) -> list[UserFullRead]:
    return await model_get(
        response, session, crud, paginator, ordering, filter_schema
    )  # type: ignore


@router.post("/users")
async def post_users(
    data: list[UserRawCreate],
    user: UserSession = Depends(get_active_superuser_dep),
    session: AsyncSession = Depends(db_session),
    crud: UserCrud = Depends(get_user_crud),
) -> int:
    ret = await crud.bulk_create(
        session,
        [
            UserCreate(
                password_hash=PwdContext.hash(ui.password),
                **ui.model_dump(exclude={"password"}),
            )
            for ui in data
        ],
    )
    await session.commit()
    return ret


@router.patch("/users/{username}")
async def patch_user(
    username: UserNameStr,
    data: UserUpdate,
    user: UserSession = Depends(get_active_superuser_dep),
    session: AsyncSession = Depends(db_session),
    crud: UserCrud = Depends(get_user_crud),
) -> int:
    return await crud.patch(
        session, [crud.model.username == username], data.to_patch(), force=True
    )


@router.delete("/users")
async def delete_users(
    user: UserSession = Depends(get_active_superuser_dep),
    ids: set[int] = Depends(get_uuid_ids_query),
    session: AsyncSession = Depends(db_session),
    crud: UserCrud = Depends(get_user_crud),
) -> int:
    return await crud.delete(session, [crud.model.id.in_(ids)], force=True)


@router.get("/user/me")
async def get_user_me(
    user_ses: UserSession = Depends(get_active_user_dep),
    session: AsyncSession = Depends(db_session),
    crud: UserCrud = Depends(get_user_crud),
) -> UserFullRead:
    return await crud.get_one(
        session, username=user_ses.user.username
    )  # noqa # type: ignore


@router.patch("/user/me")
async def patch_user_me(
    data: UserMeUpdate,
    user_ses: UserSession = Depends(get_active_user_dep),
    session: AsyncSession = Depends(db_session),
    crud: UserCrud = Depends(get_user_crud),
) -> int:
    return await crud.patch(
        session,
        [crud.model.username == user_ses.user.username],
        data.to_patch(),
        force=True,
    )  # noqa # type: ignore


@router.post("/user/register", deprecated=True)
async def post_user_register(
    data: UserRegister,
    user_ses: UserSession = Depends(get_active_user_dep),
    session: AsyncSession = Depends(db_session),
    crud: UserCrud = Depends(get_user_crud),
) -> UserFullRead:
    # NOTE: Remove this route if it isn't needed
    return await crud.create(
        session, data.to_db_schema(), force=True
    )  # noqa # type: ignore


@router.post("/auth/login")
async def post_auth_login(
    data: UserLogin,
    auth_manager: AlchemyTokenAuthService = Depends(auth_service),
    session: AsyncSession = Depends(db_session),
) -> TokenPair:
    ret = await auth_manager.login(session, data)
    await session.commit()
    return ret


@router.post("/auth/logout", status_code=204)
async def post_auth_logout(
    user_ses: UserSession = Depends(get_active_user_dep),
    session: AsyncSession = Depends(db_session),
    auth_manager: AlchemyTokenAuthService = Depends(auth_service),
):
    await auth_manager.logout(session, user_ses.raw_token)
    await session.commit()


@router.post("/auth/refresh")
async def post_auth_refresh(
    data: RefreshToken,
    auth_manager: AlchemyTokenAuthService = Depends(auth_service),
    session: AsyncSession = Depends(db_session),
) -> TokenPair:
    ret = await auth_manager.refresh(session, data.refresh_token)
    await session.commit()
    return ret


if get_settings().app.show_swagger:

    @router.post("/auth/login-form", include_in_schema=False)
    async def post_auth_login_form(
        data: Annotated[OAuth2PasswordRequestForm, Depends()],
        auth_manager: AlchemyTokenAuthService = Depends(auth_service),
        session: AsyncSession = Depends(db_session),
    ) -> TokenPair:
        ret = await auth_manager.login(
            session, UserLogin(username=data.username, password=data.password)
        )
        await session.commit()
        return ret
