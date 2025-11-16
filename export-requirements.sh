#!/usr/bin/env bash
set -e
# Export pinned requirements from poetry.lock (requires poetry-plugin-export)
poetry export -f requirements.txt --output requirements.txt --without-hashes
echo "requirements.txt generated"