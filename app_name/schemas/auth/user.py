import datetime
import uuid
from pydantic import Field, ValidationError, model_validator
from app_name.schemas.auth.token import JwtTokenSchema
from app_name.schemas.auth.types import PasswordStr, UserNameStr
from app_name.schemas.base import OrmModel
from app_name.core.crypto.passwords.base import PwdContext


class UserRegister(OrmModel):
    username: UserNameStr
    password1: PasswordStr
    password2: PasswordStr

    @model_validator(mode="after")
    def val_model(self):
        if self.password1 != self.password2:
            raise ValidationError("password1 != password2")
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
    password1: PasswordStr | None = None
    password2: PasswordStr | None = None
    is_admin: bool | None = None
    is_active: bool | None = None

    @model_validator(mode="after")
    def val_model(self):
        if (self.password1 is None and self.password2 is not None) or (
            self.password1 is not None and self.password2 is None
        ):
            raise ValidationError("password1 and password2 must be filled")
        if (
            self.password1 is not None
            and self.password2 is not None
            and self.password1 != self.password2
        ):
            raise ValidationError("password1 != password2")
        return self


class UserMeUpdate(OrmModel):
    password1: PasswordStr
    password2: PasswordStr


class UserSession(OrmModel):
    token: JwtTokenSchema  # NOTE: Injection FUCK
    user: UserFullRead
