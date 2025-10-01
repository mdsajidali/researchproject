#!/usr/bin/env bash
set -euo pipefail

# Wait for DB
if [ -n "${DB_HOST:-}" ]; then
  echo "Waiting for database at $DB_HOST:$DB_PORT..."
  for i in {1..60}; do
    if python - <<'PY' ; then
import os, socket
s=socket.socket(); s.settimeout(1.0)
s.connect((os.environ.get("DB_HOST","db"), int(os.environ.get("DB_PORT","5432"))))
print("db up")
PY
    then break; fi
    sleep 1
  done
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Optional: create a superuser in dev
if [ "${CREATE_SUPERUSER:-0}" = "1" ]; then
  python - <<'PY'
import os
from django.contrib.auth import get_user_model
from django.conf import settings
import django
django.setup()
User = get_user_model()
username=os.environ.get("DJANGO_SUPERUSER_USERNAME","admin")
email=os.environ.get("DJANGO_SUPERUSER_EMAIL","admin@example.com")
password=os.environ.get("DJANGO_SUPERUSER_PASSWORD","adminpass")
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print("Created superuser:", username)
PY
fi

exec gunicorn expense_tracker.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
