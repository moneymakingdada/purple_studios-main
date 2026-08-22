#!/usr/bin/env bash
# Render build script — runs automatically on every deploy.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py create_default_superuser

# Optional: uncomment to auto-seed demo data + purple admin theme on first deploy.
# python manage.py seed_demo
# python manage.py seed_admin_theme
