#!/usr/bin/env bash
ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"
if [ -d media ]; then
  echo "Removing media/*"
  rm -rf media/*
else
  echo "No media directory found."
fi

echo "Done."
