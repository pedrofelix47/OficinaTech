@echo off
cd /d %~dp0\..
if exist media (
  echo Deleting media\*...
  rmdir /s /q media
  mkdir media
) else (
  echo No media directory found.
)
echo Done.
