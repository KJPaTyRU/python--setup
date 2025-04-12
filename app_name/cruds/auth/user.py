from functools import cache
from app_name.config import get_settings
from app_name.core.db.postgres.crud import CrudBase
from app_name.models.auth.user import User
from app_name.schemas.auth.user import UserCreate


class UserCrud(CrudBase[User, UserCreate]):
    pass


@cache
def get_user_crud() -> UserCrud:
    return UserCrud(get_settings())
