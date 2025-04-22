from typing import TYPE_CHECKING, TypeVar
from loguru import logger
from proj_name.core.db.postgres.base import SessionMaker
from proj_name.core.exceptions import BadTokenError
from proj_name.core.socketio.namespace.base import BaseSioNamespace
from proj_name.schemas.auth.user import UserSession
from proj_name.schemas.base import OrmModel
from proj_name.services.auth.current import get_active_user

if TYPE_CHECKING:
    from proj_name.core.socketio.manager.auth import SioAuthManager


class BaseAuthCtx(OrmModel):
    user: UserSession


AuthSioCtxType = TypeVar("AuthSioCtxType", bound=BaseAuthCtx)


class BaseAuthNamespace(BaseSioNamespace[AuthSioCtxType]):

    def __init__(
        self,
        namespace: str | None = None,
        sio_auth_manager: "SioAuthManager | None" = None,
    ):
        super().__init__(namespace)
        self.auth_manager = sio_auth_manager

    def token_from_auth(self, sid: str, auth: dict | None) -> str | None:

        if not isinstance(auth, dict):
            logger.warning(
                "[{}] {} type in auth parameter for sid=`{}`",
                self.__class__.__name__,
                None if auth is None else type(auth),
                sid,
            )
            return None
        token = auth["token"]
        if not isinstance(token, str):
            logger.warning(
                "[{}] {} type of token for sid=`{}`",
                self.__class__.__name__,
                None if token is None else type(token),
                sid,
            )
            return None
        return token

    async def on_connect(self, sid: str, environ: dict, auth: dict | None):
        """
        environ: dict - dict with additional http data
        auth ~= data
        """
        logger.info(
            "[{}] Connecting client with sid=`{}`, auth={}",
            self.__class__.__name__,
            sid,
            auth,
        )
        token = None
        try:
            # TODO: add auth from query or header (for Postman). And debugcheck
            token = self.token_from_auth(sid, auth)
            if not token:
                return await self.disconnect(sid)
            async with SessionMaker() as session:
                user = await get_active_user(session, token)
                ctx = self._ctx_class(user=user)
                await self.set_context(sid, ctx)
                self.auth_manager.add_user(sid, user)

        except BadTokenError:
            token = token
            logger.info(
                "[{}] Got bad token {}", self.__class__.__name__, token
            )
            return await self.disconnect(sid)
        except Exception as e:
            logger.error(
                "[{}] Got unexpected error {}", self.__class__.__name__, e
            )
            return await self.disconnect(sid)


class AuthNamespace(BaseAuthNamespace[BaseAuthCtx]):
    pass
