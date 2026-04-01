#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h ${DB_HOST:-db} -p ${DB_PORT:-5432} -q; do
    sleep 1
done
echo "PostgreSQL is ready."

echo "Running migrations..."
python manage.py migrate --no-input

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Starting Gunicorn..."
exec gunicorn grc.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-4} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
