import datetime
import uuid
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from proj_name.cruds.auth.token import get_token_crud
from proj_name.enums import BearerTokenTypeEnum
from proj_name.models.auth.token import Token
from proj_name.schemas.auth.token import (
    JwtTokenSchema,
    TokenDbCreate,
    TokenPair,
    UserTokenExtra,
)
from proj_name.schemas.auth.user import UserFullRead
from proj_name.services.auth.jwt.base import JwtAuthLogic


class AlchemyJwtAuthLogic(JwtAuthLogic):

    def _create_token(
        self,
        token: Token,
        meta: UserTokenExtra,
        expires_delta: int,  # in minutes
        username: str,
    ) -> str:
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        jwt_token = JwtTokenSchema(
            iss=self.iss,
            sub=username,
            aud=self.aud,
            exp=now + datetime.timedelta(minutes=expires_delta),
            iat=now,
            jti=token.id,
            ttype=token.token_type,
            **meta.model_dump(),
        )

        return jwt.encode(
            jwt_token.to_payload(), self.secret, algorithm=self.algorithm
        )

    async def create_tokens(
        self, session: AsyncSession, user: UserFullRead, *args, **kwargs
    ) -> TokenPair:
        base_id = uuid.uuid4()
        (
            access_db_token,
            refresh_db_token,
        ) = await get_token_crud().bulk_create_with_return(
            session,
            [
                TokenDbCreate(
                    base_id=base_id,
                    user_id=user.id,
                    token_type=BearerTokenTypeEnum.ACCESS,
                ),
                TokenDbCreate(
                    base_id=base_id,
                    user_id=user.id,
                    token_type=BearerTokenTypeEnum.REFRESH,
                ),
            ],
        )

        return TokenPair(
            access_token=self._create_token(
                access_db_token,
                UserTokenExtra(is_admin=user.is_admin),
                self.expires_map[access_db_token.token_type],
                username=user.username,
            ),
            refresh_token=self._create_token(
                refresh_db_token,
                UserTokenExtra(is_admin=user.is_admin),
                self.expires_map[refresh_db_token.token_type],
                username=user.username,
            ),
        )
