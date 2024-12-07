#!/bin/bash

source /var/app/venv/*/bin/activate
cd /var/app/staging

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --noinput