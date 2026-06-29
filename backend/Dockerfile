# --- build stage: install dependencies ---
FROM python:3.11-slim AS build

WORKDIR /app

# Install system deps needed for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- runtime stage ---
FROM python:3.11-slim

# Install libpq for psycopg2 at runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-password --no-create-home app
WORKDIR /app

# Copy installed packages from build stage
COPY --from=build /install /usr/local

# Copy application code
COPY . .

# Collect static files
RUN DJANGO_SETTINGS_MODULE=config.settings.prod \
    SECRET_KEY=build-placeholder \
    DATABASE_URL=sqlite:///tmp.db \
    python manage.py collectstatic --noinput 2>/dev/null || true

USER app

ENV PORT=8080
ENV DJANGO_SETTINGS_MODULE=config.settings.prod
EXPOSE 8080

# Run with gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT} --workers 3 --timeout 120"]
