default: up
up:
	docker compose up db
migrate:
	alembic upgrade heads
