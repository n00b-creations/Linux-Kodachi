#!/usr/bin/env bash
# Wrapper script to run the CYBER-OS API and optionally the dashboard.
# Meant for simple developer testing. Not a production init script.

set -euo pipefail

PREFIX=${CYBER_OS_PREFIX:-/opt/cyber-os}
BIND_HOST=${CYBER_OS_BIND_HOST:-127.0.0.1}
API_PORT=${CYBER_OS_API_PORT:-8765}
LOG_DIR=${CYBER_OS_LOG_DIR:-/var/log/cyber-os}
DASHBOARD_DIR=${CYBER_OS_DASHBOARD_DIR:-$PREFIX/frontend/kdash}
START_DASHBOARD=${CYBER_OS_START_DASHBOARD:-false}

mkdir -p "$LOG_DIR"

echo "Starting CYBER-OS API on ${BIND_HOST}:${API_PORT}"
# Start uvicorn (will block). Users should run this under systemd in production.
cd "$(dirname "$0")/.." || true

# Run uvicorn with module path relative to this script
# backend.cyber_os_api:app
python3 -m uvicorn backend.cyber_os_api:app --host "$BIND_HOST" --port "$API_PORT"

# Optionally start a static file server for the dashboard (non-blocking)
if [ "$START_DASHBOARD" = "true" ]; then
  if [ -d "$DASHBOARD_DIR" ]; then
    echo "Starting dashboard static server on port 8000"
    (cd "$DASHBOARD_DIR" && python3 -m http.server 8000 &) || true
  else
    echo "Dashboard dir not found: $DASHBOARD_DIR"
  fi
fi
