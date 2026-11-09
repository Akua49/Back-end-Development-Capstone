#!/bin/sh
set -e

python manage.py makemigrations concert --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Create administrator accounts explicitly with manage.py createsuperuser.
# Never install a shared default administrator password.
exec "$@"
