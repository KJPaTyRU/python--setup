from functools import cache
from typing import Any, Callable, Sequence
from loguru import logger
from sqlalchemy import Column, Select, Table
from sqlalchemy.orm import DeclarativeBase
from proj_name.core.fastapi.filter.base import BaseFilter, BaseFilterSchema
from proj_name.core.fastapi.filter.common import FilterContext, KeyType

# A little bit messsy, but very flexible way of setting filtering logic


# * FUNCS * #
AlchemFilterOpFunc = Callable[[FilterContext, KeyType, Any], None]


def f_eq(ctx: FilterContext, k: KeyType, v: Any):
    col: Column = getattr(ctx.m, k.column_key)
    ctx.wheres.append(col == v)


def f_neq(ctx: FilterContext, k: KeyType, v: Any):
    col: Column = getattr(ctx.m, k.column_key)
    ctx.wheres.append(col != v)


def f_lt(ctx: FilterContext, k: KeyType, v: Any):
    col: Column = getattr(ctx.m, k.column_key)
    ctx.wheres.append(col < v)


def f_le(ctx: FilterContext, k: KeyType, v: Any):
    col: Column = getattr(ctx.m, k.column_key)
    ctx.wheres.append(col <= v)


def f_gt(ctx: FilterContext, k: KeyType, v: Any):
    col: Column = getattr(ctx.m, k.column_key)
    ctx.wheres.append(col > v)


def f_ge(ctx: FilterContext, k: KeyType, v: Any):
    col: Column = getattr(ctx.m, k.column_key)
    ctx.wheres.append(col >= v)


def f_null(ctx: FilterContext, k: KeyType, v: bool):
    col: Column = getattr(ctx.m, k.column_key)
    ctx.wheres.append(col.is_(None) if v else col.is_not(None))


def f_like(ctx: FilterContext, k: KeyType, v: str):
    if "%" not in v:
        v = "%" + v + "%"
    col: Column = getattr(ctx.m, k.column_key)
    ctx.wheres.append(col.like(v))


def f_not_like(ctx: FilterContext, k: KeyType, v: str):
    if "%" not in v:
        v = "%" + v + "%"
    col: Column = getattr(ctx.m, k.column_key)
    ctx.wheres.append(col.not_like(v))


def f_ilike(ctx: FilterContext, k: KeyType, v: str):
    if "%" not in v:
        v = "%" + v + "%"
    col: Column = getattr(ctx.m, k.column_key)
    ctx.wheres.append(col.ilike(v))


def f_not_ilike(ctx: FilterContext, k: KeyType, v: str):
    if "%" not in v:
        v = "%" + v + "%"
    col: Column = getattr(ctx.m, k.column_key)
    ctx.wheres.append(col.not_ilike(v))


def f_in(ctx: FilterContext, k: KeyType, v: Sequence[Any]):
    col: Column = getattr(ctx.m, k.column_key)
    ctx.wheres.append(col.in_(v))


def f_not_in(ctx: FilterContext, k: KeyType, v: Sequence[Any]):
    col: Column = getattr(ctx.m, k.column_key)
    ctx.wheres.append(col.not_in(v))


class AlchemyBaseFilter(BaseFilter):
    filter_type: str = "alch"

    # *** Fields *** #

    @classmethod
    @cache  # risky
    def _get_filter2operator(cls) -> dict[str, AlchemFilterOpFunc]:
        return {
            "": f_eq,
            #
            "eq": f_eq,
            "neq": f_neq,
            "lt": f_lt,
            "le": f_le,
            "ge": f_ge,
            "gt": f_gt,
            #
            "from": f_ge,
            "till": f_le,
            #
            "null": f_null,
            #
            "like": f_like,
            "not_like": f_not_like,
            "ilike": f_ilike,
            "not_ilike": f_not_ilike,
            #
            "in": f_in,
            "not_in": f_not_in,
        }

    def filter(
        self,
        model: type[Table | DeclarativeBase],
        stmt: Select,
        filters: BaseFilterSchema,
        *args,
        **kwargs,
    ):
        # TODO: No model - any labeled fields filter
        ctx = FilterContext(model, stmt)
        op_map = self._get_filter2operator()
        func_map = filters.func_map().get(self.filter_type, {})
        for field, value in filters.to_filter().items():
            key = KeyType(field)
            if (field, self.filter_type) in func_map:
                logger.debug(
                    "[{}] Cool! Func filter: field={}; filter={}",
                    self.__class__.__name__,
                    field,
                    filters,
                )
                func_map[key.column_key][key.operator](ctx, key, value)
            elif key.operator in op_map:
                op_map[key.operator](ctx, key, value)
        stmt = stmt.where(*ctx.wheres)
        return stmt


@cache
def get_AlchemyFilter() -> AlchemyBaseFilter:
    return AlchemyBaseFilter()
