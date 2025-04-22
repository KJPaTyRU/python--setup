from functools import cache
from typing import Literal
from fastapi import Depends, Query

from proj_name.core.fastapi.ordering.sqlalchemy import (
    AlchOrderConsturctor,
    AlchOrderingMeta,
)


@cache
def OrderingDepends(order_meta: AlchOrderingMeta):

    order_fields = []
    for oi in order_meta.ordering_fields():
        order_fields.append("-" + oi)
        order_fields.append("+" + oi)
    order_fields = Literal[tuple(order_fields)]

    def order_schema(
        order_by: list[order_fields] = Query(  # noqa # type:ignore
            default_factory=order_meta.default_order,
            description="`-` - descending; `+` - ascending",
        )
    ) -> AlchOrderConsturctor:
        return AlchOrderConsturctor(order_by, order_meta)

    return Depends(order_schema, use_cache=True)
