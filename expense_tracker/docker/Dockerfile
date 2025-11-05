# syntax=docker/dockerfile:1
FROM python:3.11-slim

# --- Runtime envs (safe defaults)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# --- System deps (psycopg2, wait-for checks, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# --- App directory
WORKDIR /app

# --- Leverage layer caching for deps
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy project
COPY . /app

# Ensure entrypoint is executable
RUN chmod +x /app/entrypoint.sh

# --- OpenShift-friendly permissions
# Do NOT set a fixed USER. Instead, make everything group-writable and
# set group to 0 so any arbitrary UID (with GID=0) can run in OCP/MicroShift.
RUN chgrp -R 0 /app && chmod -R g=u /app

# --- Django settings module (your project name)
# If your settings module path is different, update this env.
ENV DJANGO_SETTINGS_MODULE=expense_tracker.settings

# --- Bake static files at build time to generate the manifest
# (prevents "Missing staticfiles manifest entry" at runtime)
RUN python manage.py collectstatic --noinput

# --- Port & entrypoint
EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]

