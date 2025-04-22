from functools import cache
import socketio

from app_name.core.socketio.manager.auth import SioAuthManager
from app_name.core.socketio.namespace.auth import AuthNamespace


@cache
def create_socketio_server():
    # client_manager = socketio.AsyncRedisManager(logger=logger)
    client_manager = socketio.AsyncManager()

    sio = socketio.AsyncServer(
        client_manager=client_manager,
        async_mode="asgi",
        # namespaces=["*"]
    )
    sio.register_namespace(AuthNamespace("/user", SioAuthManager()))
    return sio
