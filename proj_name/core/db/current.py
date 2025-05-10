from proj_name.core.db.postgres.crud import CrudBase, ModelCreateT, ModelT
from proj_name.core.fastapi.ordering.sqlalchemy import AlchCrudedOrderingMeta


class OrderedCrudBase(CrudBase[ModelT, ModelCreateT]):

    def __init__(self, settings):
        super().__init__(settings)
        self.set_ordering_meta(AlchCrudedOrderingMeta(self))
