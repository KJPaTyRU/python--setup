from functools import cache

from sqlalchemy import Select, select
from sqlalchemy.orm import joinedload
from app_name.config import get_settings
from app_name.core.db.postgres.crud import CrudBase
from app_name.models.auth.token import Token
from app_name.schemas.auth.token import TokenDbCreate


class TokenCrud(CrudBase[Token, TokenDbCreate]):

    @property
    def _select_model(self) -> Select:
        """can be used for config options with inload"""
        return select(self._model).options(joinedload(self._model.user))


@cache
def get_token_crud() -> TokenCrud:
    return TokenCrud(get_settings())
