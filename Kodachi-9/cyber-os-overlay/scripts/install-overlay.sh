#!/usr/bin/env bash
set -euo pipefail

PREFIX="${CYBER_OS_PREFIX:-/opt/cyber-os}"
CONFIG="${CYBER_OS_CONFIG:-/etc/cyber-os}"
STATE="${CYBER_OS_STATE:-/var/lib/cyber-os}"
LOG="${CYBER_OS_LOG:-/var/log/cyber-os}"
DESKTOP="${CYBER_OS_DESKTOP:-/usr/share/applications/cyber-os.desktop}"
SOURCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this installer as root." >&2
  exit 1
fi

if [[ ! -f /etc/os-release ]]; then
  echo "Cannot identify the host distribution." >&2
  exit 1
fi

. /etc/os-release

if [[ "${ID_LIKE:-}" != *debian* && "${ID:-}" != "debian" && "${ID:-}" != "kodachi" ]]; then
  echo "CYBER-OS Phase 1 requires a Debian-family host; refusing to modify the system." >&2
  exit 1
fi

install -d -m 0755 "$PREFIX" "$PREFIX/backend" "$PREFIX/config" "$PREFIX/integrations" "$PREFIX/plugins" "$PREFIX/scripts"
install -d -m 0755 "$CONFIG" "$STATE" "$LOG"

cp -a "$SOURCE_ROOT/backend/." "$PREFIX/backend/"
cp -a "$SOURCE_ROOT/config/." "$PREFIX/config/"
cp -a "$SOURCE_ROOT/integrations/." "$PREFIX/integrations/"
cp -a "$SOURCE_ROOT/plugins/." "$PREFIX/plugins/"
cp -a "$SOURCE_ROOT/scripts/cyber-os-api.sh" "$PREFIX/scripts/"
chmod 0755 "$PREFIX/scripts/cyber-os-api.sh"

cat > "$CONFIG/runtime.env" <<EOF
CYBER_OS_CONFIG_ROOT=$CONFIG
CYBER_OS_STATE_ROOT=$STATE
CYBER_OS_LOG_ROOT=$LOG
EOF
chmod 0644 "$CONFIG/runtime.env"

cat > "$DESKTOP" <<EOF
[Desktop Entry]
Name=CYBER-OS
Comment=Kodachi Cyber Operations Overlay
Exec=$PREFIX/scripts/cyber-os-api.sh
Terminal=true
Type=Application
Categories=Security;System;
EOF
chmod 0644 "$DESKTOP"

cat > "$STATE/install-manifest" <<EOF
prefix=$PREFIX
config=$CONFIG
state=$STATE
log=$LOG
desktop=$DESKTOP
source_commit=phase1
EOF
chmod 0644 "$STATE/install-manifest"

echo "CYBER-OS overlay installed without replacing Kodachi-owned files."
echo "Runtime prefix: $PREFIX"
echo "Configuration:   $CONFIG"
echo "State:            $STATE"
echo "Logs:             $LOG"
echo "Desktop entry:    $DESKTOP"
