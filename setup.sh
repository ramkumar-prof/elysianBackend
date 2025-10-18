#!/bin/sh

# Exit immediately if a command fails
set -e

DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-3306}

echo "=== setup.sh started ==="
echo "Waiting for database at $DB_HOST:$DB_PORT..."

counter=0
until nc -z "$DB_HOST" "$DB_PORT"; do
  counter=$((counter+1))
  echo "[${counter}] Database not ready yet, sleeping 2s..."
  sleep 2
done

echo "Database is up! Proceeding..."

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn elysianBackend.wsgi:application --bind 0.0.0.0:8000
