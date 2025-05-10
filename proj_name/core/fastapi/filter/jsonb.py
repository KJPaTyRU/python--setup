from functools import cache
from typing import TYPE_CHECKING, Any
from sqlalchemy import Column
from sqlalchemy.sql import operators

from proj_name.core.fastapi.filter.base import BaseFilterSchema

if TYPE_CHECKING:
    from proj_name.core.fastapi.filter.common import FilterContext, KeyType
    from proj_name.core.fastapi.filter.sqlalchemy import AlchemFilterOpFunc


jb_operator = operators.custom_op("->>")


def f_jb_eq(ctx: "FilterContext", k: "KeyType", v: Any):
    col: Column = getattr(ctx.m, "data")
    ctx.wheres.append(jb_operator(col, k.column_key) == v)


def f_jb_neq(ctx: "FilterContext", k: "KeyType", v: Any):
    col: Column = getattr(ctx.m, "data")
    ctx.wheres.append(jb_operator(col, k.column_key) != v)


def f_jb_like(ctx: "FilterContext", k: "KeyType", v: Any):
    col: Column = getattr(ctx.m, "data")
    if "%" not in v:
        v = "%" + v + "%"
    ctx.wheres.append(jb_operator(col, k.column_key).like(v))


def f_jb_not_like(ctx: "FilterContext", k: "KeyType", v: Any):
    col: Column = getattr(ctx.m, "data")
    if "%" not in v:
        v = "%" + v + "%"
    ctx.wheres.append(jb_operator(col, k.column_key).not_like(v))


def f_jb_ilike(ctx: "FilterContext", k: "KeyType", v: Any):
    col: Column = getattr(ctx.m, "data")
    if "%" not in v:
        v = "%" + v + "%"
    ctx.wheres.append(jb_operator(col, k.column_key).ilike(v))


def f_jb_not_ilike(ctx: "FilterContext", k: "KeyType", v: Any):
    col: Column = getattr(ctx.m, "data")
    if "%" not in v:
        v = "%" + v + "%"
    ctx.wheres.append(jb_operator(col, k.column_key).not_ilike(v))


def f_jb_in(ctx: "FilterContext", k: "KeyType", v: Any):
    col: Column = getattr(ctx.m, "data")
    ctx.wheres.append(jb_operator(col, k.column_key).in_(v))


def f_jb_not_in(ctx: "FilterContext", k: "KeyType", v: Any):
    col: Column = getattr(ctx.m, "data")
    ctx.wheres.append(jb_operator(col, k.column_key).not_in(v))


class CrashliticsZipFilter(BaseFilterSchema):

    device_id: str | None = None
    device_id__neq: str | None = None
    device_id__ilike: str | None = None
    device_id__not_ilike: str | None = None
    device_id__in: set[str] | None = None
    device_id__not_in: set[str] | None = None

    @classmethod
    @cache
    def jsonb_map(cls) -> dict[str, "AlchemFilterOpFunc"]:
        return {
            "": f_jb_eq,
            #
            "eq": f_jb_eq,
            "neq": f_jb_neq,
            #
            "like": f_jb_like,
            "not_like": f_jb_not_like,
            "ilike": f_jb_ilike,
            "not_ilike": f_jb_not_ilike,
            #
            "in": f_jb_in,
            "not_in": f_jb_not_in,
        }

    @classmethod
    def func_map(cls) -> dict[str, dict[str, dict[str, "AlchemFilterOpFunc"]]]:
        """
        Returns:
            dict[tuple[str,str], Callable] - it's a dict with
                keys of (`field_name`, `filter_type`) and values of any
                filter func. `filter_type` is a name of filter group (like:
                SQLAlchemy, MongoDb, etc)
        """
        jb_map = cls.jsonb_map()
        return {"alch": {"device_id": jb_map}}
