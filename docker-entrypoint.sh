#!/usr/bin/env sh

# Ожидаем поднятия базы, иначе придется перезапускать сервис
./wait-for-db.sh ${DB_HOST}:${DB_PORT}

python3 manage.py migrate --no-input
python3 manage.py makemigrations
python3 manage.py migrate --no-input
python3 manage.py collectstatic --no-input
python3 manage.py shell -c "from kip_api.models import User; User.objects.create_superuser('admin@admin.com', 'admin')"
django-admin compilemessages

gunicorn kip.wsgi:application -w 3 -b 0.0.0.0:${PORT:-8000}
