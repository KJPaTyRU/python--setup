#!/bin/bash

echo "Starting App with entrypoint.sh"


if [ "${MIGRATE:-0}" -eq 1 ]; then
  echo "Migrating db"
  uv run --no-dev alembic upgrade heads

  if [ $? -eq 0 ]; then
    echo "DB migrated!"
  else
    echo "SWW. Cannot migrate database"
  fi

fi

exec "$@"
