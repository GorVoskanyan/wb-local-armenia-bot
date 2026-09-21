#!/usr/bin/env bash
set -e

echo "Running Alembic migrations..."
alembic upgrade head

echo "Seeding initial mock database..."
python scripts/seed_data.py || true

echo "Starting application..."
exec "$@"
