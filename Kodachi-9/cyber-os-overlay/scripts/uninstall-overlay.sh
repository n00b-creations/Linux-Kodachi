#!/usr/bin/env bash
set -euo pipefail

PREFIX="${CYBER_OS_PREFIX:-/opt/cyber-os}"
CONFIG="${CYBER_OS_CONFIG:-/etc/cyber-os}"
STATE="${CYBER_OS_STATE:-/var/lib/cyber-os}"
LOG="${CYBER_OS_LOG:-/var/log/cyber-os}"
DESKTOP="${CYBER_OS_DESKTOP:-/usr/share/applications/cyber-os.desktop}"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this uninstaller as root." >&2
  exit 1
fi

rm -f "$DESKTOP"
rm -rf "$PREFIX" "$CONFIG" "$STATE" "$LOG"

echo "CYBER-OS overlay removed. Kodachi-owned system files were not modified by this uninstaller."
