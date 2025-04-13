from pydantic import BaseModel, ConfigDict, Field


class PageLimitParams(BaseModel):
    model_config = ConfigDict(frozen=True, validate_default=False)
    page: int = Field(ge=1)
    limit: int = Field(ge=1)


class OffsetLimitParams(BaseModel):
    model_config = ConfigDict(frozen=True, validate_default=False)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1)


class BasePaginator:
    def __init__(
        self, page_limit: int, cur_params: PageLimitParams | None = None
    ):
        self.page_limit = page_limit
        self.cur_params = cur_params

    def page2offset(self, params: PageLimitParams) -> OffsetLimitParams:
        limit = min(self.page_limit, params.limit)
        offset = (params.page - 1) * limit
        return OffsetLimitParams(offset, limit)

    def paginate(self, *args, **kwargs):
        """Paginate query function"""
        raise NotImplementedError()
