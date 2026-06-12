@echo off
REM Reset script for Windows: backup DB, remove DB, clear media, migrate, create superuser
SETLOCAL ENABLEDELAYEDEXPANSION
cd /d %~dp0\..
set TIMESTAMP=%DATE:~6,4%%DATE:~3,2%%DATE:~0,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
if exist db.sqlite3 (
  echo Backing up db.sqlite3 to db.sqlite3.bak.%TIMESTAMP%
  copy db.sqlite3 db.sqlite3.bak.%TIMESTAMP% >nul
)
if exist db.sqlite3 (
  echo Deleting db.sqlite3
  del /f /q db.sqlite3
)
if exist media (
  echo Deleting media\*
  rmdir /s /q media
  mkdir media
)
echo Running migrations
python -m pip install -r requirements.txt || echo pip install failed
python manage.py migrate --noinput

nset ADMIN_USER=%DELIVER_ADMIN_USER%
if "%ADMIN_USER%"=="" set ADMIN_USER=admin
set ADMIN_EMAIL=%DELIVER_ADMIN_EMAIL%
if "%ADMIN_EMAIL%"=="" set ADMIN_EMAIL=admin@example.com
set ADMIN_PASS=%DELIVER_ADMIN_PASS%
if "%ADMIN_PASS%"=="" set ADMIN_PASS=adminpass

npython - <<PY
from django.contrib.auth.models import User
if not User.objects.filter(username='%ADMIN_USER%').exists():
    User.objects.create_superuser('%ADMIN_USER%','%ADMIN_EMAIL%','%ADMIN_PASS%')
    print('Superuser created: %ADMIN_USER%')
else:
    print('Superuser already exists: %ADMIN_USER%')
PY

echo Reset complete
