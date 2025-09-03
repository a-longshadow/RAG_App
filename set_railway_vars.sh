#!/bin/bash
# Set Railway environment variables following Railway's Django documentation

echo "Setting Railway environment variables..."

# Set Railway's standard PostgreSQL variables (these reference the Postgres service)
railway variables --set PGDATABASE='${{Postgres.PGDATABASE}}'
railway variables --set PGUSER='${{Postgres.PGUSER}}'
railway variables --set PGPASSWORD='${{Postgres.PGPASSWORD}}'
railway variables --set PGHOST='${{Postgres.PGHOST}}'
railway variables --set PGPORT='${{Postgres.PGPORT}}'

# Set Django-specific variables
railway variables --set DJANGO_SUPERUSER_USERNAME=admin
railway variables --set DJANGO_SUPERUSER_EMAIL=admin@ragapp.com  
railway variables --set DJANGO_SUPERUSER_PASSWORD=AdminRAG2025

echo "Railway environment variables set following official documentation!"
echo "Admin login credentials:"
echo "Username: admin"
echo "Password: AdminRAG2025"
