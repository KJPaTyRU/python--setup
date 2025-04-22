# Base FastApi project

## Socket.io notes

### Основные понятия для работы с socket.io:
 - url: http://localhost:8015/test - это адрес сервер (http/https/ws/
 wss + host:port) и namespace (/test). На namespace НИКАК не влияют
 настройки роутинга (mount, proxy и т.д.. namespace - всегда namespace, а не путь)

 - socketio_path: /ws/socket.io - реальный путь, по которому будет
 происходить подключение к socket.io серверу (на него влияют mount,
 proxy). Для кастомного путь питонячегого socket.io сервера (в связке с
 fastapi) необходимо в ASGIApp указывать socketio_path равный prefix в
 FastAPI.mount. К строке с кастомным путем НЕ НАДО добавлять socket.io -
 оно автоматом добавится (т.е. если socketio_path='/very/strange/
 path' JS клиентам надо подключаться по '/very/strange/path/socket.io')

## Before development
1) pip install uv
2) uv add pre-commit
3) uv run pre-commit install

**Check pre-commit**:
`uv run pre-commit run --show-diff-on-failure --color=always --all-files`
