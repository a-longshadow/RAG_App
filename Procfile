release: python manage.py migrate && python manage.py collectstatic --noinput && python manage.py ensure_superuser
web: gunicorn django_rag.wsgi:application --bind 0.0.0.0:$PORT --workers 4
