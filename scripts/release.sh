#!/bin/bash
set -e

echo "🚀 Starting Release Script..."

echo "📦 Applying database migrations..."
python manage.py migrate

echo "📜 Seeding Legislation 2025..."
python scripts/seed_legislation_2025.py

echo "🌱 Seeding Demo Scenarios..."
python scripts/seed_scenarios.py

echo "✅ Release process complete!"

echo "🚀 Starting Gunicorn Server..."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} config.wsgi:application
