#!/usr/bin/env bash
# install-overlay.sh
# Installs CYBER-OS overlay files to the filesystem.
# Run as root to install system-wide. For testing, run as non-root to create local dirs.

set -euo pipefail

PREFIX=${1:-/opt/cyber-os}
ETC_DIR=${2:-/etc/cyber-os}
STATE_DIR=${3:-/var/lib/cyber-os}
LOG_DIR=${4:-/var/log/cyber-os}

echo "Installing CYBER-OS overlay to $PREFIX"

install -d -m 0755 "$PREFIX"
install -d -m 0755 "$PREFIX/scripts"
install -d -m 0755 "$PREFIX/frontend"
install -d -m 0755 "$ETC_DIR"
install -d -m 0755 "$STATE_DIR"
install -d -m 0755 "$LOG_DIR"

# Copy scripts from repo (assumes running from project root)
SRCDIR="$(pwd)/Kodachi-9/cyber-os-overlay"
if [ -d "$SRCDIR" ]; then
  cp -a "$SRCDIR/backend" "$PREFIX/" || true
  cp -a "$SRCDIR/scripts" "$PREFIX/" || true
  cp -a "$SRCDIR/frontend" "$PREFIX/" || true
  cp -a "$SRCDIR/integrations" "$PREFIX/" || true
  chmod -R 0755 "$PREFIX/scripts" || true
  find "$PREFIX/backend" -type f -name "*.py" -exec chmod 0644 {} + || true
fi

# Install systemd unit if possible
if [ "$EUID" -eq 0 ]; then
  if command -v systemctl >/dev/null 2>&1; then
    echo "Installing systemd service"
    install -m 0644 "$PREFIX/scripts/systemd/cyber-os-api.service" /etc/systemd/system/cyber-os-api.service || true
    systemctl daemon-reload || true
    systemctl enable --now cyber-os-api.service || true
  else
    echo "systemctl not found; skipping systemd install"
  fi
else
  echo "Not running as root; skipped systemd install"
fi

echo "Installation complete."
