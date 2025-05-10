from functools import cache
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

if TYPE_CHECKING:
    from proj_name.core.fastapi.filter.sqlalchemy import AlchemFilterOpFunc


class BaseFilterSchema(BaseModel):
    """Important NOTE:

    Use `fastapi.Query(None)` as default value for any pydantic scehma.
    With this approach you can pass any other Query parameters into the
    FastApi route.
    """

    def to_filter(self) -> dict[str, Any]:
        return self.model_dump(
            mode="python", exclude_none=True, exclude_unset=True
        )

    @classmethod
    def func_map(cls) -> dict[str, dict[str, dict[str, "AlchemFilterOpFunc"]]]:
        """
        Returns:
            dict[tuple[str,str], Callable] - it's a dict with
                keys of (`field_name`, `filter_type`) and values of any
                filter func. `filter_type` is a name of filter group (like:
                SQLAlchemy, MongoDb, etc)
        """
        return {}


class BaseFilter:
    filter_type: str = "base"

    @classmethod
    @cache  # risky
    def _get_filter2operator(cls) -> dict[str, Any]:
        raise NotImplementedError()

    def filter(self, *args, **kwargs):
        raise NotImplementedError()
