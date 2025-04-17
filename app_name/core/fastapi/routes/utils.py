import datetime
import uuid
from fastapi import Query, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app_name.core.db.postgres.crud import CrudBase, ModelCreateT, ModelT
from app_name.core.fastapi.filter.base import BaseFilterSchema
from app_name.core.fastapi.filter.sqlalchemy import (
    AlchemyBaseFilter,
    get_AlchemyFilter,
)
from app_name.core.fastapi.ordering.sqlalchemy import AlchOrderConsturctor
from app_name.core.fastapi.pagination.sqlalchemy import AlchemyBasePaginator

TOTAL_COUNT_HEADER = "X-Total-Count"
BOUND_DATE_FROM_HEADER = "X-Date-From"
BOUND_DATE_TILL_HEADER = "X-Date-Till"


class BaseHeaderDate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    x_max_date: datetime.datetime | None = Field(
        serialization_alias=BOUND_DATE_TILL_HEADER
    )
    x_min_date: datetime.datetime | None = Field(
        serialization_alias=BOUND_DATE_FROM_HEADER
    )

    @property
    def headers(self):
        return self.model_dump(mode="json", by_alias=True, exclude_none=True)


def get_int_ids_query(ids: set[int] = Query(min_length=1)) -> set[int]:
    return ids


def get_uuid_ids_query(
    ids: set[uuid.UUID] = Query(min_length=1),
) -> set[uuid.UUID]:
    return ids


async def get_bound_dates(
    session: AsyncSession,
    crud: CrudBase[ModelT, ModelCreateT],
    filter_schema: BaseFilterSchema,
    filter_class: AlchemyBaseFilter = get_AlchemyFilter(),
) -> BaseHeaderDate:
    """
    Returns:
        tuple(date-from, date-till)
    """
    bd_stmt = crud.date_bounds()
    bd_stmt = filter_class.filter(crud._model, bd_stmt, filter_schema)

    res = (await session.execute(bd_stmt)).first()
    return BaseHeaderDate.model_validate(res)


async def get_count(session: AsyncSession, stmt: Select) -> int:
    count_stmt = select(func.count()).select_from(stmt.subquery("count_sq"))
    return (await session.execute(count_stmt)).scalar_one()


async def model_get(
    response: Response,
    session: AsyncSession,
    crud: CrudBase[ModelT, ModelCreateT],
    paginator: AlchemyBasePaginator,
    ordering: AlchOrderConsturctor,
    filter_schema: BaseFilterSchema,
    /,
    add_total_count_header: bool = True,
    add_bound_date_header: bool = True,
    *,
    select_stmt: Select | None = None,
    filter_class: AlchemyBaseFilter = get_AlchemyFilter(),
) -> list[ModelT]:
    stmt = select_stmt or crud._select_model

    stmt = filter_class.filter(crud._model, stmt, filter_schema)
    if add_total_count_header:
        response.headers[TOTAL_COUNT_HEADER] = str(
            await get_count(session, stmt)
        )
    if add_bound_date_header and crud.bond_date_enabled:
        boarders = await get_bound_dates(
            session, crud, filter_schema, filter_class
        )
        response.headers.update(boarders.headers)

    stmt = ordering.order(stmt)
    stmt = paginator.paginate(stmt)
    ret_objs = (await session.execute(stmt)).scalars().all()

    return ret_objs  # noqa # type: ignore
