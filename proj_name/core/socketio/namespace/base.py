from typing import Generic, Literal, TypeVar, Union
from loguru import logger
import socketio

from proj_name.schemas.base import OrmModel

# https://socket.io/docs/v4/client-socket-instance/#disconnect
ReasonStr = Literal[
    "client disconnect",
    "server disconnect",
    "ping timeout",
    "transport close",
    "transport error",
]
EDataType = Union[dict, str, bytes]
# Ack - it is a value, that will be returned on emit call
AckType = EDataType | None
SioCtxType = TypeVar("SioCtxType", bound=OrmModel)


class BaseSioNamespace(socketio.AsyncNamespace, Generic[SioCtxType]):
    def __init__(self, namespace: str | None = None):
        """
        namespace: str = '/my-custom-namespace'. namespace is used in uri
        """
        super().__init__(namespace)

        base = self.__orig_bases__[0]
        self._ctx_class: type[SioCtxType] = base.__args__[0]

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

    async def on_disconnect(self, sid: str, reason: ReasonStr):
        logger.info(
            "[{}] Disconnecting client with sid=`{}`, reason={}",
            self.__class__.__name__,
            sid,
            reason,
        )

    async def on_ping(self, sid: str, *datas: EDataType) -> AckType:
        logger.info(
            "[{}] Got `{}` event from client with sid=`{}`, data={}",
            self.__class__.__name__,
            "ping",
            sid,
            datas,
        )
        if not datas:
            return "no data pong"
        elif len(datas) >= 2:
            return "too many data pong"
        data: EDataType = datas[0]  # noqa # type: ignore
        match data:
            case str():
                return "pong"
            case dict():
                return dict(pong=True)
            case bytes():
                return b"pong"
            case _:
                logger.warning(
                    "[{}] Unexpected data from sid=`{}` type type(`{}`)={}",
                    self.__class__.__name__,
                    sid,
                    type(data),
                    data,
                )
                return "unexpected pong"

    # Context functions
    async def set_context(self, sid: str, ctx: SioCtxType, **kwargs):
        ctx_data = ctx.model_dump(mode="python")
        await self.save_session(sid, ctx_data)

    async def get_context(self, sid: str) -> SioCtxType:
        return self._ctx_class.model_validate(await self.get_session(sid))

    async def clear_context(self, sid: str):
        # TODO: How to clear this???
        await self.save_session(sid, {})
