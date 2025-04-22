import datetime
import uuid

from pydantic import Field
from proj_name.enums import BearerTokenTypeEnum
from proj_name.schemas.base import OrmModel


class TokenDbCreate(OrmModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    base_id: uuid.UUID
    user_id: uuid.UUID
    token_type: BearerTokenTypeEnum


class TokenDbRead(OrmModel):
    id: uuid.UUID
    user_id: uuid.UUID
    base_id: uuid.UUID
    token_type: BearerTokenTypeEnum


# https://en.wikipedia.org/wiki/JSON_Web_Token
class BaseJwtToken(OrmModel):
    iss: str  # proj_name
    sub: str  # username
    aud: str  # proj_name
    exp: datetime.datetime
    iat: datetime.datetime
    jti: uuid.UUID  # token_id


class UserTokenExtra(OrmModel):
    is_admin: bool = False


class JwtTokenSchema(BaseJwtToken, UserTokenExtra):
    ttype: BearerTokenTypeEnum

    def token_id(self) -> uuid.UUID:
        return self.jti

    def token_type(self) -> BearerTokenTypeEnum:
        return self.ttype

    def to_payload(self) -> dict:
        ret = self.model_dump(mode="json", exclude={"exp", "iat"})
        ret["exp"] = int(self.exp.timestamp())
        ret["iat"] = int(self.iat.timestamp())
        return ret


class TokenPair(OrmModel):
    access_token: str
    refresh_token: str
    type: str = "Bearer"


class RefreshToken(OrmModel):
    refresh_token: str
    type: str = "Bearer"
