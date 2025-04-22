from functools import cache
from proj_name.config import get_settings
from proj_name.core.db.current import OrderedCrudBase
from proj_name.models.auth.user import User
from proj_name.schemas.auth.user import UserCreate


class UserCrud(OrderedCrudBase[User, UserCreate]):
    @cache
    def ordering_fields(self) -> list[str]:
        return ["id", "username", "log_time", "is_admin", "is_active"]

    @cache
    def default_order(self) -> list[str]:
        return ["-id"]


@cache
def get_user_crud() -> UserCrud:
    return UserCrud(get_settings())
