#!/usr/bin/env bash
# assets/fetch_rich_model.sh
# Download a richer GLB model into the frontend assets directory.

set -euo pipefail

ASSET_DIR="${1:-./assets/models}"
mkdir -p "$ASSET_DIR"
TARGET="$ASSET_DIR/dashboard_model_rich.glb"

# A moderate-size, well-formed glb from Khronos sample models (Avocado)
URL="https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Avocado/glTF-Binary/Avocado.glb"

echo "Downloading rich dashboard model to $TARGET"
if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$URL" -o "$TARGET"
elif command -v wget >/dev/null 2>&1; then
  wget -qO "$TARGET" "$URL"
else
  echo "No curl/wget available to download model; please fetch it manually to $TARGET"
  exit 0
fi

echo "Downloaded model size: $(stat -c%s "$TARGET" 2>/dev/null || echo 'unknown') bytes"
