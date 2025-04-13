from typing import AsyncGenerator

from pydantic import BaseModel
from sqlalchemy import JSON, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from app_name.config import get_settings

DbEngine = create_async_engine(
    get_settings().db_url, echo=get_settings().log.level == "TRACE"
)
SessionMaker = async_sessionmaker(DbEngine, expire_on_commit=False)


async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionMaker() as session:
        yield session


class BasePydanticType(TypeDecorator):
    """
    Example:
    ```
    class DocDataType(BasePydanticType):
        @classmethod
        def get_pydantic_schema(cls) -> type[DocDataSchema]:
            return DocDataSchema
    ```
    """

    impl = JSON

    @classmethod
    def get_pydantic_schema(cls) -> type[BaseModel]:
        raise NotImplementedError()

    def load_dialect_impl(self, dialect):
        # Use JSONB for PostgreSQL and JSON for other databases.
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())

    def process_bind_param(self, value, dialect) -> dict | None:
        # to db type
        if value is None:
            return None
        if isinstance(value, BaseModel):
            return value.model_dump()
        elif isinstance(value, dict):
            return value
        raise ValueError(f"Unexpected type. Got {value.__class__}")

    def process_result_value(self, value, dialect):
        # to python type
        if value is None:
            return value
        if isinstance(value, dict):
            return self.get_pydantic_schema().model_validate(value)
        elif isinstance(value, BaseModel):
            return value
        raise ValueError(f"Unexpected type. Got {value.__class__}")
