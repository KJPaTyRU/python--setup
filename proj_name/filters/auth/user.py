import datetime

from proj_name.core.fastapi.filter.base import BaseFilterSchema


class UserFilter(BaseFilterSchema):
    username: str | None = None
    username__neq: str | None = None
    username__ilike: str | None = None
    username__not_ilike: str | None = None
    username__in: set[str] | None = None
    username__not_in: set[str] | None = None

    is_admin: bool | None = None
    is_ative: bool | None = None
    is_ative__in: set[bool] | None = None  # Remove

    log_time__from: datetime.datetime | None = None
    log_time__till: datetime.datetime | None = None

    updated_at__from: datetime.datetime | None = None
    updated_at__till: datetime.datetime | None = None
