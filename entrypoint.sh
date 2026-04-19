#!/usr/bin/env sh
set -eu

cd /app/chile

python manage.py check

exec python manage.py runserver 0.0.0.0:8000
