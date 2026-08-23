#!/usr/bin/env bash
set -euo pipefail

PREFIX="${CYBER_OS_PREFIX:-/opt/cyber-os}"
CONFIG="${CYBER_OS_CONFIG:-/etc/cyber-os}"

fail=0

check_path() {
  local path="$1"
  if [[ -e "$path" ]]; then
    printf 'PASS  %s\n' "$path"
  else
    printf 'FAIL  %s\n' "$path"
    fail=1
  fi
}

check_path "$PREFIX/backend/cyber_os_api.py"
check_path "$PREFIX/scripts/cyber-os-api.sh"
check_path "$CONFIG/runtime.env"
check_path "/usr/share/applications/cyber-os.desktop"

if [[ "$fail" -ne 0 ]]; then
  echo "CYBER-OS overlay health check failed." >&2
  exit 1
fi

echo "CYBER-OS overlay health check passed."
