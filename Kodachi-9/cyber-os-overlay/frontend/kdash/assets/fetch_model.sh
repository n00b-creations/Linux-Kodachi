#!/usr/bin/env bash
# assets/fetch_model.sh
# Download a sample GLB dashboard model into the frontend assets directory.
# Intended to be run by the installer (or manually) after copying files to PREFIX.

set -euo pipefail

ASSET_DIR="${1:-./assets/models}"
mkdir -p "$ASSET_DIR"
TARGET="$ASSET_DIR/dashboard_model.glb"

# Small sample model (Khronos Cube sample). Replace with your rich model later.
URL="https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Cube/glTF-Binary/Cube.glb"

echo "Downloading dashboard model to $TARGET"
if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$URL" -o "$TARGET"
elif command -v wget >/dev/null 2>&1; then
  wget -qO "$TARGET" "$URL"
else
  echo "No curl/wget available to download model; please fetch it manually to $TARGET"
  exit 0
fi

echo "Downloaded model size: $(stat -c%s "$TARGET" 2>/dev/null || echo 'unknown') bytes"
