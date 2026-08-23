#!/usr/bin/env bash
set -euo pipefail

PREFIX="${CYBER_OS_PREFIX:-/opt/cyber-os}"
HOST="${CYBER_OS_BIND_HOST:-127.0.0.1}"
PORT="${CYBER_OS_API_PORT:-8765}"

exec python3 -m uvicorn cyber_os_api:app \
  --app-dir "$PREFIX/backend" \
  --host "$HOST" \
  --port "$PORT" \
  --no-server-header
