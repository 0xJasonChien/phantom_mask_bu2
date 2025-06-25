uv run python manage.py collectstatic --noinput
uv run python manage.py migrate --noinput
uv run python manage.py load_pharmacies
uv run python manage.py load_members
uv run gunicorn core.wsgi:application --bind 0.0.0.0:8000
