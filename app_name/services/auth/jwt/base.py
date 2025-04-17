import datetime
from functools import cache
import jwt
from loguru import logger
from app_name.core.exceptions import TokenParseError, TokenValidationError
from app_name.enums import BearerTokenTypeEnum
from app_name.schemas.auth.token import JwtTokenSchema
from app_name.schemas.auth.user import UserFullRead, UserSession
from app_name.services.auth.base import AuthLogic


def create_expires_map(acces_dt: int, refresh_dt: int):
    # dt in minutes
    return {
        BearerTokenTypeEnum.ACCESS: acces_dt,
        BearerTokenTypeEnum.REFRESH: refresh_dt,
    }


@cache
def get_leeway() -> int:
    dt = datetime.datetime.now().astimezone()
    utc_dt = datetime.datetime.utcoffset(dt)
    if utc_dt is None:
        return 0
    return int(utc_dt.total_seconds())


class JwtAuthLogic(AuthLogic):
    def __init__(
        self,
        iss: str,
        aud: str,
        secret: str,
        expires_map: dict,
        algorithm: str = "HS256",
    ):
        self.iss = iss
        self.aud = aud
        self.secret = secret
        self.algorithm = algorithm
        self.expires_map = expires_map

    def parse_token(
        self, token: str | bytes, *args, **kwargs
    ) -> JwtTokenSchema:
        try:
            data = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                audience=self.aud,
                issuer=self.iss,
                verify=True,
                # leeway=get_leeway(),
            )
            logger.debug(f"{data=}")
            return JwtTokenSchema.model_validate(data)
        except Exception as e:
            logger.debug("Token parse error")
            raise TokenParseError(token=token) from e

    def validate(
        self,
        token: JwtTokenSchema,
        user_session: UserFullRead,
        raw_token: str,
        *args,
        **kwargs,
    ) -> UserSession:
        if user_session.password_updated_at > token.iat:
            raise TokenValidationError()
        return UserSession(token=token, raw_token=raw_token, user=user_session)
