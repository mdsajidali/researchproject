# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# leverage docker layer caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . /app
#COPY entrypoint.sh /app/entrypoint.sh
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh


# create non-root user
#RUN useradd -m appuser && chown -R appuser:appuser /app
#USER appuser

# collect static at runtime (entrypoint will run migrations etc.)
ENV DJANGO_SETTINGS_MODULE=expense_tracker.settings
EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
