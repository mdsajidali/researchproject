#!/usr/bin/env bash
set -euo pipefail

# Wait for DB
# Wait for DB
if [ -n "${DB_HOST:-}" ]; then
  echo "Waiting for database at $DB_HOST:${DB_PORT:-5432}..."
  for i in {1..60}; do
    python <<PY
import os, socket, sys
s = socket.socket(); s.settimeout(1.0)
try:
    s.connect((os.environ.get("DB_HOST", "db"), int(os.environ.get("DB_PORT", "5432"))))
    print("db up")
    sys.exit(0)
except Exception as e:
    sys.exit(1)
PY
    if [ $? -eq 0 ]; then
      break
    fi
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
