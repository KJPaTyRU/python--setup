import datetime
import re
from uuid import UUID
import uuid

from sqlalchemy import BigInteger, DateTime, Uuid, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)

REGULAR_COMP = re.compile(r"((?<=[a-z\d])[A-Z]|(?!^)[A-Z](?=[a-z]))")


SYSTEM_DEFAULT_ROLES = ["System default"]


def camel_to_snake(camel_string):
    return REGULAR_COMP.sub(r"_\1", camel_string).lower()


class BaseDbModel(DeclarativeBase):
    @classmethod
    def __generate_table_snake_name(cls):
        """StupidCAMelCase to stupid_ca_mel_case"""
        return camel_to_snake(cls.__name__)

    @classmethod
    def _get_prefix(cls) -> str:
        """StupidCAMelCase to stupid_ca_mel_case"""
        return "lm"

    @declared_attr
    def __tablename__(cls) -> str:
        """this is a class method"""
        return f"{cls._get_prefix()}_{cls.__generate_table_snake_name()}"


class IdBaseDbModel(BaseDbModel):
    __abstract__ = True
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)


class UuidBaseDbModel(BaseDbModel):
    __abstract__ = True
    id: Mapped[UUID] = mapped_column(
        Uuid(), default=uuid.uuid4, primary_key=True
    )


class DbLogMixin:
    __abstract__ = True
    log_time: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), server_default=func.now(), index=True, nullable=False
    )


class CreatedAtMixin:
    __abstract__ = True
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), nullable=False
    )
