#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input --clear
python manage.py migrate
# Création automatique du superutilisateur (si inexistant)
export DJANGO_SUPERUSER_PASSWORD="HamzaImmo2026"
export DJANGO_SUPERUSER_USERNAME="Hamza"
export DJANGO_SUPERUSER_EMAIL="hamzabelrhouzi1@gmail.com"

python manage.py createsuperuser --no-input || true