#!/bin/bash
# Railway post-deployment script
# Run migrations and collect static files after the database is available

echo "Running Django migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Railway deployment setup complete!"
