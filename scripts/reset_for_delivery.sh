#!/usr/bin/env bash
# Safe reset script for delivery: backups DB, clears uploads, recreates DB and creates admin user.
set -euo pipefail
ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

TIMESTAMP=$(date +%Y%m%d%H%M%S)
if [ -f db.sqlite3 ]; then
  echo "Backing up db.sqlite3 -> db.sqlite3.bak.$TIMESTAMP"
  cp db.sqlite3 "db.sqlite3.bak.$TIMESTAMP"
fi

# Remove database file to start fresh
if [ -f db.sqlite3 ]; then
  echo "Removing db.sqlite3"
  rm db.sqlite3
fi

# Remove media uploads if present
if [ -d media ]; then
  echo "Removing media/*"
  rm -rf media/* || true
fi

# Recreate database schema
echo "Running migrations"
python -m pip install -r requirements.txt --quiet || true
python manage.py migrate --noinput

# Create a default superuser (change these values or set env variables before running)
ADMIN_USER=${DELIVER_ADMIN_USER:-admin}
ADMIN_EMAIL=${DELIVER_ADMIN_EMAIL:-admin@example.com}
ADMIN_PASS=${DELIVER_ADMIN_PASS:-adminpass}

python - <<PY
from django.contrib.auth.models import User
if not User.objects.filter(username='${ADMIN_USER}').exists():
    User.objects.create_superuser('${ADMIN_USER}', '${ADMIN_EMAIL}', '${ADMIN_PASS}')
    print('Superuser created: ${ADMIN_USER}')
else:
    print('Superuser already exists: ${ADMIN_USER}')
PY

echo "Reset complete. Backup (if any) saved as db.sqlite3.bak.*"
