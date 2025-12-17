
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
# gcc and libpq-dev might be needed if we switch to Postgres later
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Collect static files (Essential for Whitenoise)
RUN python manage.py collectstatic --noinput

# Run server using Gunicorn, binding to the PORT environment variable (Railway requirement)
# Also runs migrations automatically on startup to ensure DB schema and data are up to date
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn --bind 0.0.0.0:${PORT:-8000} config.wsgi:application"]
