default: up
up:
	docker compose up db
migrate:
	alembic upgrade heads
make-migrations:
	alembic revision --autogenerate -m "$m"
