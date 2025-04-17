from typing import Any, Generic, TypeVar

__doc__ = """
BaseOrderingMeta - It is a schema of ordering_fields, default_order and order
    field_name to column (or logic) mapper. Use it only for declaring fields
    for ordering and mapping.

BaseOrderConsturctor - It is an adapter for your db with instruction for
    applying ordering to the final stmt. Use it with final BaseOrderingMeta for
    specific database.
"""


class BaseOrderingMeta:
    # @cache
    def ordering_fields(self) -> list[str]:
        """
        Example:
        ```
        return ['id','username']
        ```
        """
        raise NotImplementedError()

    # @cache
    def default_order(self) -> list[str]:
        """
        Example:
        ```
        return ['-id','+username']
        ```
        """
        return [f"-{self.ordering_fields()[0]}"]

    # @cache
    def order_map(self) -> dict[str, Any]:
        """
        Example:
        ```
        ret: dict[str, UnaryExpression] = {}
        for ori in self.ordering_fields():
            col: Column = getattr(self.model, ori)
            ret["-" + ori] = col.desc()
            ret["+" + ori] = col.asc()
        return ret
        ```
        """
        raise NotImplementedError()


OrderingMetaT = TypeVar("OrderingMetaT", bound=BaseOrderingMeta)


class BaseOrderConsturctor(Generic[OrderingMetaT]):
    def __init__(self, cur_order: list[str], order_meta: OrderingMetaT):
        self.cur_order: list[str] = cur_order or order_meta.default_order()
        self.order_meta: OrderingMetaT = order_meta

    def order(self, *args, **kwargs):
        raise NotImplementedError()
