# Base FastApi project

## Features

 - Сборка проекта в компактный Docker-образ и развертывание проекта через docker compose
 - Крассивый и стандартизированный код за счет `pre-commit`
 - Простой модуль авторизации для FastApi и Socket.io
 - Возожожность задавать конфиги не только из .env, но из yaml, toml, json
 - Менеджер пакетов `uv`
 - Middleware для обработки ошибок
 - CRUD для работы с PostgreSQL
   - Фильтрация результатов выдачи
   - Сортировка результатов выдачи
   - Пагинация результатов выдачи

## Usage

1) Заменить все вхождения `proj_name` на имя вашего проекта
(в VsCode через `Ctrl + Shift + F` можно открыть меню поиска и замены)
2) Переименовать корневой проект с `proj_name` на имя вашего проекта

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
