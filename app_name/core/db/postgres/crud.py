from functools import cache
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from loguru import logger
from sqlalchemy import (
    ColumnExpressionArgument,
    CursorResult,
    Delete,
    Select,
    Update,
    bindparam,
    delete,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import Insert, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app_name.core.exceptions import (
    AppException,
    BadCreateDataException,
    BadFilterException,
    BadSchemaException,
    DbException,
)
from app_name.models.base import BaseDbModel
from app_name.schemas.base import OrmModel

if TYPE_CHECKING:
    from app_name.config import Settings

ModelT = TypeVar("ModelT", bound=BaseDbModel)
ModelCreateT = TypeVar("ModelCreateT", bound=OrmModel)

SQLWhereType = ColumnExpressionArgument[bool]
SQLOrderByType = ColumnExpressionArgument[Any]


def filters_to_wheres(model: type[ModelT], filters: Any):
    res = []
    try:
        for k, v in filters.items():
            res.append(getattr(model, k) == v)
    except Exception as e:
        raise BadFilterException(model=model.__name__, filters=filters) from e
    return res


class BulkCrudMixin:

    @property
    def _delete_stmt(
        self: "BulkCrudMixin | CrudBase[ModelT, ModelCreateT]",
    ) -> Delete | Update:
        """can be used for config options with inload
        Update Example:
        ```
        update(self._model).where(self._model.delete == false()).values(
            delete=true()).returning(self._model.id
        )
        ```
        """
        return delete(self._model)

    @cache
    def get_pks_fields(
        self: "BulkCrudMixin | CrudBase[ModelT, ModelCreateT]",
    ) -> list[str]:
        return ["id"]

    @cache
    def get_pks_where(
        self: "BulkCrudMixin | CrudBase[ModelT, ModelCreateT]",
    ) -> list[SQLWhereType]:
        return [
            getattr(self._model, pi) == bindparam(pi)
            for pi in self.get_pks_fields()
        ]

    def stmt_bulk_upsert(
        self: "BulkCrudMixin | CrudBase[ModelT, ModelCreateT]", stmt: Insert
    ) -> Insert:
        pks = self.get_pks_fields()
        return stmt.on_conflict_do_update(
            index_elements=[getattr(self._model, pi) for pi in pks],
            set_={k: getattr(stmt.excluded, k) for k in pks},
        )

    @classmethod
    def sync_create_schema_converter(cls, datas: list[Any]) -> list[dict]:
        insert_data = []
        for di in datas:
            match di:
                case OrmModel():
                    insert_data.append(di.to_db())
                case dict():
                    insert_data.append(di)
                case _:
                    logger.debug(
                        "[{}] Bad create di={}; datas={}",
                        cls.__name__,
                        di,
                        datas,
                    )
                    raise BadCreateDataException(data=datas, bad_data=di)
        return insert_data

    async def get_multi(
        self: "BulkCrudMixin | CrudBase[ModelT, ModelCreateT]",
        session: AsyncSession,
        /,
        wheres: list[SQLWhereType],
        offset: int = 0,
        limit: int | None = None,
        order_by: list[SQLOrderByType] | None = None,
        unique: bool = False,
        **filters: Any,
    ) -> list[ModelT]:
        try:
            expressions = []
            expressions.extend(wheres)
            if filters:
                expressions.extend(filters_to_wheres(self._model, filters))
            stmt = self._select_model.where(*expressions)
            if offset:
                stmt = stmt.offset(offset)
            if limit:
                stmt = stmt.limit(limit)
            if order_by:
                stmt = stmt.order_by(*order_by)
            res = await session.execute(stmt)
            if unique:
                res = res.unique()
            res = res.scalars().all()
            return res
        except AppException:
            raise
        except SQLAlchemyError as e:
            raise DbException() from e

    async def bulk_create_with_return(
        self: "BulkCrudMixin | CrudBase[ModelT, ModelCreateT]",
        session: AsyncSession,
        /,
        datas: list[dict[str, Any] | ModelCreateT],
    ) -> list[ModelT]:
        """More requests..."""
        insert_data = self.sync_create_schema_converter(datas)
        stmt = insert(self._model).values(insert_data).returning(self._model)
        return (await session.execute(stmt)).scalars().all()

    async def bulk_create(
        self: "BulkCrudMixin | CrudBase[ModelT, ModelCreateT]",
        session: AsyncSession,
        /,
        datas: list[dict[str, Any] | ModelCreateT],
    ) -> int:
        insert_data = self.sync_create_schema_converter(datas)
        stmt = insert(self._model).values(insert_data)
        res = await session.execute(stmt)
        return res.rowcount

    async def bulk_update(
        self: "BulkCrudMixin | CrudBase[ModelT, ModelCreateT]",
        session: AsyncSession,
        /,
        datas: list[dict[str, Any] | ModelCreateT],
    ) -> int:
        insert_data = self.sync_create_schema_converter(datas)
        stmt = (
            update(self._model)
            .where(*self.get_pks_where())
            .values(insert_data)
        )
        res = await session.execute(stmt)
        return res.rowcount

    async def bulk_upsert(
        self: "BulkCrudMixin | CrudBase[ModelT, ModelCreateT]",
        session: AsyncSession,
        /,
        datas: list[dict[str, Any] | ModelCreateT],
    ) -> int:
        insert_data = self.sync_create_schema_converter(datas)
        stmt = insert(self._model).values(insert_data)
        stmt = self.stmt_bulk_upsert(stmt)
        res = await session.execute(stmt)
        return res.rowcount

    async def delete(
        self: "BulkCrudMixin | CrudBase[ModelT, ModelCreateT]",
        session: AsyncSession,
        /,
        wheres: list[SQLWhereType] | None = None,
        force: bool = False,
        **filters: Any,
    ) -> int:
        try:
            expressions = []
            if wheres:
                expressions.extend(wheres)
            if filters:
                expressions.extend(filters_to_wheres(self._model, filters))
            stmt = self._delete_stmt.where(*expressions)
            res = (await session.execute(stmt)).rowcount

            if force:
                await session.commit()
            else:
                await session.flush()
            return res
        except AppException:
            raise
        except SQLAlchemyError as e:
            raise DbException() from e


class CrudBase(BulkCrudMixin, Generic[ModelT, ModelCreateT]):

    def __init__(self, settings: "Settings"):
        self.settings = settings
        base = self.__orig_bases__[0]
        model, create_schema = base.__args__[:2]
        self._model: type[ModelT] = model
        self._create_schema: ModelCreateT = create_schema

    @property
    def _select_model(self) -> Select:
        """can be used for config options with inload"""
        return select(self._model)

    async def create(
        self,
        session: AsyncSession,
        /,
        data: dict[str, Any] | ModelCreateT,
        force: bool = False,
    ) -> ModelT:
        try:
            if isinstance(data, OrmModel):
                data = data.to_db()
            if not isinstance(data, dict):
                raise BadSchemaException(data=data, data_type=type(data))

            instance = self._model(**data)
            session.add(instance)
            if force:
                await session.commit()
            else:
                await session.flush([instance])
            await session.refresh(instance)
            return instance

        except AppException:
            raise
        except SQLAlchemyError as e:
            raise DbException() from e

    async def get_one_or_none(
        self,
        session: AsyncSession,
        /,
        wheres: list[SQLWhereType] | None = None,
        **filters: Any,
    ) -> ModelT | None:
        try:
            expressions = []
            if wheres:
                expressions.extend(wheres)
            if filters:
                expressions.extend(filters_to_wheres(self._model, filters))
            stmt = self._select_model.where(*expressions)
            res = (await session.execute(stmt)).scalar_one_or_none()
            return res
        except AppException:
            raise
        except SQLAlchemyError as e:
            raise DbException() from e

    async def get_one(
        self,
        session: AsyncSession,
        /,
        wheres: list[SQLWhereType] | None = None,
        **filters: Any,
    ) -> ModelT:
        try:
            expressions = []
            if wheres:
                expressions.extend(wheres)
            if filters:
                expressions.extend(filters_to_wheres(self._model, filters))
            stmt = self._select_model.where(*expressions)

            res = (await session.execute(stmt)).scalar_one()
            return res
        except AppException:
            raise
        except SQLAlchemyError as e:
            raise DbException() from e

    async def patch(
        self,
        session: AsyncSession,
        /,
        wheres: list[SQLWhereType],
        data: dict[str, Any],
        force: bool = False,
    ) -> int:
        try:
            data = {k: v for k, v in data.items() if v is not None}
            stmt = update(self._model).where(*wheres).values(**data)
            res: CursorResult = await session.execute(stmt)
            if force:
                await session.commit()
            else:
                await session.flush()
            return res.rowcount
        except AppException:
            raise
        except SQLAlchemyError as e:
            raise DbException() from e

    async def upsert(
        self,
        session: AsyncSession,
        /,
        data: dict[str, Any] | ModelCreateT,
        filter_fields: list[str],
        force: bool = False,
    ) -> ModelT:
        try:
            if isinstance(data, OrmModel):
                data = data.to_db()
            if not isinstance(data, dict):
                raise BadSchemaException(data=data, data_type=type(data))
            filters = {k: data[k] for k in filter_fields}
            instance = self.get_one_or_none(session, **filters)
            if instance is None:
                return await self.create(session, data, force)
            # else
            for k, v in data.items():
                setattr(instance, k, v)
            if force:
                await session.commit()
            else:
                await session.flush([instance])
            await session.refresh(instance)
            return instance
        except AppException:
            raise
        except SQLAlchemyError as e:
            raise DbException() from e


"""
class UserModel(CrudBase[User, UserCreateSchema])
    pass
"""
