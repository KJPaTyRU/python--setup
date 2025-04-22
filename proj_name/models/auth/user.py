import datetime
from sqlalchemy import Boolean, DateTime, String, Text, false, func, true
from sqlalchemy.orm import Mapped, mapped_column
from proj_name.models.auth.base import AuthBaseDbModel
from proj_name.models.base import DbLogMixin, UuidBaseDbModel


class User(UuidBaseDbModel, DbLogMixin, AuthBaseDbModel):
    username: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    password_hash: Mapped[str] = mapped_column(Text())

    password_updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(True), server_default=func.now(), nullable=False
    )

    is_admin: Mapped[bool] = mapped_column(
        Boolean(), index=True, server_default=false()
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean(), index=True, server_default=true()
    )
