#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
cd vinateria_3_hermanos
python manage.py collectstatic --noinput
# Si tienes migraciones y DB en Render: python manage.py migrate