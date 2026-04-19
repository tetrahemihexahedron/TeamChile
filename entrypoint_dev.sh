#!/usr/bin/env sh
set -eu

cd /app/chile

python manage.py check

# Dev-only: create migration files locally
# migrate is idempotent if the DB is already up to date.
python manage.py makemigrations chile --noinput
python manage.py migrate --noinput

# load the fixture if it hasn't already been loaded
if python manage.py shell -c "
from chile.models import Buyer
import sys
sys.exit(0 if Buyer.objects.exists() else 1)
"
then
  echo 'Fixture already loaded'
else
  echo 'Loading fixture'
  python manage.py loaddata fixtures/data.json
fi

# python manage.py collectstatic --noinput

# create a superuser if one doesn't exist
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(is_superuser=True).exists() or User.objects.create_superuser('admin', 'admin@test.dev', 'pass')"

exec python manage.py runserver 0.0.0.0:8000
