from functools import cache
from sqlalchemy import Select
from typing_extensions import Self
from fastapi import Query
from proj_name.core.fastapi.pagination.base import (
    BasePaginator,
    PageLimitParams,
)


class AlchemyBasePaginator(BasePaginator):

    def from_query(self):
        def query_func(
            page: int = Query(1, ge=1),
            limit: int = Query(self.page_limit, ge=1),
        ) -> Self:
            return self.__class__(
                self.page_limit, PageLimitParams(page=page, limit=limit)
            )

        return query_func

    def paginate(self, stmt: Select) -> Select:
        if self.cur_params is None:
            return stmt
        rparams = self.page2offset(self.cur_params)
        return stmt.offset(rparams.offset).limit(rparams.limit)


@cache
def paginator1000() -> AlchemyBasePaginator:
    return AlchemyBasePaginator(1000)
