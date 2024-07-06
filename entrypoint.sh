#!/bin/bash

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

echo "Starting Gunicorn."
# Start the server
echo "Starting server..."
exec "$@"
