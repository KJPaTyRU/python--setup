from fastapi import FastAPI
from socketio import ASGIApp

from app_name.core.socketio.current import create_socketio_server


def add_sio_to_fastapi(app: FastAPI, path: str = "/ws") -> FastAPI:
    sio = create_socketio_server()
    asgi_sio = ASGIApp(sio, socketio_path=path)
    app.mount(path, asgi_sio)
    return app
