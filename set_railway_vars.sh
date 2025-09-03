#!/bin/bash
# Set Railway environment variables for Django superuser

echo "Setting Railway environment variables..."

railway variables --set DJANGO_SUPERUSER_USERNAME=admin
railway variables --set DJANGO_SUPERUSER_EMAIL=admin@ragapp.com  
railway variables --set DJANGO_SUPERUSER_PASSWORD=AdminRAG2025

echo "Environment variables set! Deploy the app and you can login with:"
echo "Username: admin"
echo "Password: AdminRAG2025"
