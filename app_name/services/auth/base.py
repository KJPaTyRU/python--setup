from typing import Generic, Protocol, TypeVar
import uuid

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app_name.core.crypto.passwords.base import PwdContext
from app_name.core.exceptions import (
    BadLoginCredsError,
    BadTokenError,
    TokenValidationError,
)
from app_name.cruds.auth.token import get_token_crud
from app_name.cruds.auth.user import get_user_crud
from app_name.enums import BearerTokenTypeEnum
from app_name.schemas.auth.token import TokenPair
from app_name.schemas.auth.user import UserFullRead, UserLogin, UserSession


class AuthLogicTokenProtocol(Protocol):
    sub: str  # username

    def token_id(self) -> uuid.UUID: ...  # noqa # type: ignore
    def token_type(self) -> BearerTokenTypeEnum: ...  # noqa # type: ignore


class AuthLogic:

    def parse_token(
        self, token: str | bytes, *args, **kwargs
    ) -> AuthLogicTokenProtocol:
        raise NotImplementedError()

    def validate(self, *args, **kwargs):
        raise NotImplementedError()

    async def create_tokens(self, *args, **kwargs):
        raise NotImplementedError()


AuthLogicT = TypeVar("AuthLogicT", bound=AuthLogic)


class AuthService(Generic[AuthLogicT]):
    def __init__(self, auth_logic: AuthLogicT):
        self.auth_logic: AuthLogicT = auth_logic

    async def auth(self, *args, **kwargs) -> UserSession:
        raise NotImplementedError()

    async def login(self, *args, **kwargs):
        raise NotImplementedError()

    async def logout(self, *args, **kwargs):
        raise NotImplementedError()

    async def refresh(self, *args, **kwargs):
        raise NotImplementedError()

    async def extra_login(self, *args, **kwargs):
        """After login flow function"""
        raise NotImplementedError()


class AlchemyTokenAuthService(AuthService[AuthLogicT]):

    async def auth(
        self, session: AsyncSession, token: str | bytes, *args, **kwargs
    ) -> UserSession:
        logger.debug("[{}] Got token {}", self.__class__.__name__, token)
        token_data = self.auth_logic.parse_token(token)

        if token_data.token_type() is not BearerTokenTypeEnum.ACCESS:
            logger.debug(
                "[{}] No access token type ({})",
                self.__class__.__name__,
                token,
            )
            raise BadTokenError(token=token)
        token_id = token_data.token_id()
        db_token = await get_token_crud().get_one_or_none(session, id=token_id)
        if db_token is None:
            logger.debug(
                "[{}] Token {}, not found in db",
                self.__class__.__name__,
                token_id,
            )
            raise BadTokenError(token=token)

        if db_token.token_type is not BearerTokenTypeEnum.ACCESS:
            logger.debug(
                "[{}] No db access token type ({})",
                self.__class__.__name__,
                token,
            )
            raise BadTokenError(token=token)
        try:
            return self.auth_logic.validate(
                token_data, UserFullRead.model_validate(db_token.user), token
            )
        except TokenValidationError as e:
            logger.debug(e)
            await get_token_crud().delete(
                session, base_id=db_token.base_id, force=True
            )
            raise BadTokenError() from e

    async def login(
        self, session: AsyncSession, data: UserLogin, *args, **kwargs
    ) -> TokenPair:
        user = await get_user_crud().get_one_or_none(
            session, username=data.username
        )
        if user is None:
            logger.debug(
                "[{}] Trying to login via unregistered user `{}`",
                self.__class__.__name__,
                data.username,
            )
            raise BadLoginCredsError()
        if not PwdContext.verify(data.password, user.password_hash):
            logger.debug(
                "[{}] Trying to login to user `{}` with wrong password",
                self.__class__.__name__,
                data.username,
            )
            raise BadLoginCredsError()
        res: TokenPair = await self.auth_logic.create_tokens(
            session, UserFullRead.model_validate(user)
        )
        return await self.extra_login(session, res, *args, **kwargs)

    async def logout(
        self, session: AsyncSession, token: str | bytes, *args, **kwargs
    ):
        logger.debug("[{}] Got token {}", self.__class__.__name__, token)
        token_data = self.auth_logic.parse_token(token)
        if token_data.token_type() is not BearerTokenTypeEnum.ACCESS:
            logger.debug(
                "[{}] No access token type ({})",
                self.__class__.__name__,
                token,
            )
            raise BadTokenError(token=token)
        token_id = token_data.token_id()
        crud = get_token_crud()
        db_token = await crud.get_one_or_none(session, id=token_id)
        if db_token is None:
            logger.debug(
                "[{}] Token {}, not found in db",
                self.__class__.__name__,
                token_id,
            )
            raise BadTokenError(token=token)
        ret = await crud.delete(session, base_id=db_token.base_id, force=True)
        logger.debug("[{}] {} tokens deleted", self.__class__.__name__, ret)

    async def extra_login(
        self, session: AsyncSession, res: TokenPair, *args, **kwargs
    ) -> TokenPair:
        return res

    async def refresh(
        self, session: AsyncSession, token: str, *args, **kwargs
    ):
        logger.debug(
            "[{}] Got refresh token {}", self.__class__.__name__, token
        )
        token_data = self.auth_logic.parse_token(token)
        if token_data.token_type() is not BearerTokenTypeEnum.REFRESH:
            logger.debug(
                "[{}] No refresh token type ({})",
                self.__class__.__name__,
                token,
            )
            raise BadTokenError(token=token)
        token_id = token_data.token_id()
        crud = get_token_crud()
        db_token = await crud.get_one_or_none(session, id=token_id)

        if db_token is None:
            logger.debug(
                "[{}] Token refresh {}, not found in db",
                self.__class__.__name__,
                token_id,
            )
            raise BadTokenError(token=token)
        if db_token.token_type is not BearerTokenTypeEnum.REFRESH:
            logger.debug(
                "[{}] No db refresh token type ({})",
                self.__class__.__name__,
                token,
            )
            raise BadTokenError(token=token)

        await crud.delete(session, base_id=db_token.base_id, force=False)

        user = await get_user_crud().get_one_or_none(
            session, username=token_data.sub
        )
        res: TokenPair = await self.auth_logic.create_tokens(
            session, UserFullRead.model_validate(user)
        )
        return await self.extra_login(session, res, *args, **kwargs)
