from functools import cache
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import Enum, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app_name.enums import BearerTokenTypeEnum
from app_name.models.auth.base import AuthBaseDbModel
from app_name.models.base import DbLogMixin

if TYPE_CHECKING:
    from app_name.models.auth.user import User


@cache
def get_User() -> "type[User]":
    from app_name.models.auth.user import User

    return User


class Token(DbLogMixin, AuthBaseDbModel):
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), default=uuid.uuid4, primary_key=True
    )
    base_id: Mapped[uuid.UUID] = mapped_column(Uuid(), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(get_User().id, ondelete="CASCADE"), index=True
    )
    token_type: Mapped[BearerTokenTypeEnum] = mapped_column(
        Enum(BearerTokenTypeEnum), index=True
    )

    user: Mapped["User"] = relationship()
