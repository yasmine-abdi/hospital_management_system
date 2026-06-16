#!/usr/bin/env bash
# Exit on error
set -o errexit

# Rakib dhammaan maktabadaha
pip install -r requirements.txt

# Uruuri faylasha static-ka ah
python manage.py collectstatic --no-input

# U soco migrate-ka database-ka
python manage.py migrate