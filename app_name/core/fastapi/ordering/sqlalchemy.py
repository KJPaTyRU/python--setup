# pyright: reportIncompatibleMethodOverride=false
from functools import cache
from typing import TYPE_CHECKING
from sqlalchemy import Column, Select, UnaryExpression

from app_name.core.fastapi.ordering.base import (
    BaseOrderConsturctor,
    BaseOrderingMeta,
)

if TYPE_CHECKING:
    from app_name.core.db.postgres.crud import CrudBase


class AlchOrderingMeta(BaseOrderingMeta):
    def ordering_fields(self) -> list[str]:
        raise NotImplementedError()

    def default_order(self) -> list[str]:
        return [f"-{self.ordering_fields()[0]}"]

    def order_map(self) -> dict[str, UnaryExpression]:
        raise NotImplementedError()


class AlchCrudedOrderingMeta(AlchOrderingMeta):
    def __init__(self, crud: "CrudBase"):
        self._crud = crud

    def ordering_fields(self) -> list[str]:
        return self._crud.ordering_fields()

    def default_order(self) -> list[str]:
        return self._crud.default_order()

    @cache
    def order_map(self) -> dict[str, UnaryExpression]:
        ret: dict[str, UnaryExpression] = {}
        for ori in self.ordering_fields():
            col: Column = getattr(self._crud.model, ori)
            ret["-" + ori] = col.desc()
            ret["+" + ori] = col.asc()
        return ret


class AlchOrderConsturctor(BaseOrderConsturctor[AlchOrderingMeta]):

    def order(self, stmt: Select, *args, **kwargs) -> Select:
        orders = []
        order_map = self.order_meta.order_map()
        for coi in self.cur_order:
            orders.append(order_map[coi])
        return stmt.order_by(*orders)
