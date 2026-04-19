#!/usr/bin/env sh
set -eu

cd /app/chile

python manage.py check

# python manage.py collectstatic --noinput

# create a superuser if one doesn't exist
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(is_superuser=True).exists() or User.objects.create_superuser('admin', 'admin@test.dev', 'pass')"

exec python manage.py runserver 0.0.0.0:8000
