Reset / Delivery instructions
=============================

These scripts help you prepare the project for delivery by removing test data and recreating the database.

POSIX (Linux/macOS):

```
cd <repo-root>
./scripts/reset_for_delivery.sh
```

Windows (cmd.exe):

```
cd <repo-root>
scripts\reset_for_delivery.bat
```

Scripts will:
- backup `db.sqlite3` to `db.sqlite3.bak.<timestamp>` if present
- delete `db.sqlite3`
- remove files under `media/`
- run `python manage.py migrate`
- create a default superuser (`admin` / `admin@example.com` / `adminpass`) unless you set env vars:
  - `DELIVER_ADMIN_USER`, `DELIVER_ADMIN_EMAIL`, `DELIVER_ADMIN_PASS`

Settings changes
----------------
- `oficinatech/settings.py` now reads `SECRET_KEY`, `DJANGO_DEBUG` and `DJANGO_ALLOWED_HOSTS` from environment variables if present.

Security note: rotate any secrets before publishing the repo publicly.
