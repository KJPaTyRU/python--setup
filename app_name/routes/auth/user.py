from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app_name.core.crypto.passwords.base import PwdContext
from app_name.core.db.postgres.base import db_session
from app_name.core.fastapi.filter.depends import FilterDepends
from app_name.core.fastapi.pagination.sqlalchemy import (
    AlchemyBasePaginator,
    paginator1000,
)
from app_name.core.fastapi.routes.utils import get_uuid_ids_query, model_get
from app_name.cruds.auth.user import UserCrud, get_user_crud
from app_name.filters.auth.user import UserFilter
from app_name.schemas.auth.user import (
    UserCreate,
    UserFullRead,
    UserMeUpdate,
    UserRawCreate,
    UserRegister,
)

router = APIRouter(prefix="", tags=["User & Auth"])


def user_router() -> APIRouter:
    return router


@router.get("/users-no-count")
async def get_users_no_count(
    response: Response,
    session: AsyncSession = Depends(db_session),
    crud: UserCrud = Depends(get_user_crud),
    paginator: AlchemyBasePaginator = Depends(paginator1000),
    filter_schema: UserFilter = FilterDepends(UserFilter),
) -> list[UserFullRead]:
    return await model_get(
        response,
        session,
        crud,
        paginator,
        filter_schema,
        add_bound_date_header=False,
        add_total_count_header=False,
    )  # type: ignore


@router.get("/users")
async def get_users(
    response: Response,
    session: AsyncSession = Depends(db_session),
    crud: UserCrud = Depends(get_user_crud),
    paginator: AlchemyBasePaginator = Depends(paginator1000),
    filter_schema: UserFilter = FilterDepends(UserFilter),
) -> list[UserFullRead]:
    return await model_get(
        response,
        session,
        crud,
        paginator,
        filter_schema,
        add_bound_date_header=False,
    )  # type: ignore


@router.post("/users")
async def post_users(
    data: list[UserRawCreate],
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


@router.delete("/users")
async def delete_users(
    ids: set[int] = Depends(get_uuid_ids_query),
    session: AsyncSession = Depends(db_session),
    crud: UserCrud = Depends(get_user_crud),
) -> int:
    return await crud.delete(session, [crud.model.id.in_(ids)], force=True)


@router.get("/user/me")
async def get_user_me(
    session: AsyncSession = Depends(db_session),
    crud: UserCrud = Depends(get_user_crud),
) -> UserFullRead:
    # TODO: Update with auth
    username = "admin"
    return await crud.get_one(session, username=username)  # type: ignore


@router.patch("/user/me")
async def patch_user_me(
    data: UserMeUpdate,
    session: AsyncSession = Depends(db_session),
    crud: UserCrud = Depends(get_user_crud),
) -> int:
    # TODO: Update with auth
    username = "admin"
    return await crud.patch(
        session, [crud.model.username == username], data.to_patch(), force=True
    )  # noqa # type: ignore


@router.post("/user/register")
async def post_user_register(
    data: UserRegister,
    session: AsyncSession = Depends(db_session),
    crud: UserCrud = Depends(get_user_crud),
) -> UserFullRead:
    return await crud.create(
        session, data.to_db_schema(), force=True
    )  # noqa # type: ignore
