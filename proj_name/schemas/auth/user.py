import datetime
import uuid
from pydantic import Field, model_validator
from proj_name.schemas.auth.token import JwtTokenSchema
from proj_name.schemas.auth.types import PasswordStr, UserNameStr
from proj_name.schemas.base import OrmModel
from proj_name.core.crypto.passwords.base import PwdContext


class UserRegister(OrmModel):
    username: UserNameStr
    password1: PasswordStr
    password2: PasswordStr

    @model_validator(mode="after")
    def val_model(self):
        if self.password1 != self.password2:
            raise ValueError("password1 != password2")
        return self

    def to_db_schema(self) -> "UserCreate":
        return UserCreate(
            password_hash=PwdContext.hash(self.password1),
            **self.model_dump(exclude={"password1", "password2"}),
        )


class UserAdminRegister(UserRegister):
    is_admin: bool = False
    is_active: bool = True


class UserLogin(OrmModel):
    username: UserNameStr
    password: PasswordStr


class UserRawCreate(OrmModel):
    username: UserNameStr
    password: str = Field(min_length=1)

    is_admin: bool = False
    is_active: bool = True


class UserCreate(OrmModel):
    username: UserNameStr
    password_hash: str = Field(min_length=1)

    is_admin: bool = False
    is_active: bool = True


class UserFullRead(OrmModel):
    id: uuid.UUID
    username: str
    password_updated_at: datetime.datetime = Field(exclude=True)
    updated_at: datetime.datetime
    is_admin: bool
    is_active: bool


class UserUpdate(OrmModel):
    password1: PasswordStr | None = Field(None, exclude=True)
    password2: PasswordStr | None = Field(None, exclude=True)
    is_admin: bool | None = None
    is_active: bool | None = None

    @model_validator(mode="after")
    def val_model(self):
        if (self.password1 is None and self.password2 is not None) or (
            self.password1 is not None and self.password2 is None
        ):
            raise ValueError("password1 and password2 must be filled")
        if (
            self.password1 is not None
            and self.password2 is not None
            and self.password1 != self.password2
        ):
            raise ValueError("password1 != password2")
        return self

    def to_patch(self) -> dict:
        ret = self.model_dump(
            mode="python", exclude_unset=True, exclude_none=True
        )
        if (
            self.password1
            and self.password2
            and self.password1 == self.password2
        ):
            ret["password_hash"] = PwdContext.hash(self.password1)
        return ret


class UserMeUpdate(OrmModel):
    password1: PasswordStr
    password2: PasswordStr

    def to_patch(self) -> dict:
        return UserUpdate.model_validate(self).to_patch()


class UserSession(OrmModel):
    raw_token: str
    token: JwtTokenSchema  # NOTE: Injection FUCK
    user: UserFullRead
