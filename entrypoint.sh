#!/bin/bash

python manage.py migrate

echo "Starting Gunicorn."
exec gunicorn phantom_wrap.config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --access-logfile - --error-logfile - --log-level info
    "$@"
