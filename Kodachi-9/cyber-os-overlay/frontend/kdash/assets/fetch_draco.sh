#!/usr/bin/env bash
# assets/fetch_draco.sh
# Download DRACO decoder files required for DRACO-compressed glTFs to assets/draco

set -euo pipefail

DRACO_DIR="${1:-./assets/draco}"
mkdir -p "$DRACO_DIR"

# Files taken from the three.js examples draco decoder bundle (smalljs + wasm)
DRACO_JS="https://www.gstatic.com/draco/versioned/decoders/1.4.1/draco_decoder.js"
DRACO_WASM="https://www.gstatic.com/draco/versioned/decoders/1.4.1/draco_decoder.wasm"

echo "Downloading draco decoder into $DRACO_DIR"
if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$DRACO_JS" -o "$DRACO_DIR/draco_decoder.js"
  curl -fsSL "$DRACO_WASM" -o "$DRACO_DIR/draco_decoder.wasm"
elif command -v wget >/dev/null 2>&1; then
  wget -qO "$DRACO_DIR/draco_decoder.js" "$DRACO_JS"
  wget -qO "$DRACO_DIR/draco_decoder.wasm" "$DRACO_WASM"
else
  echo "No curl/wget available to download draco decoder; please fetch manually to $DRACO_DIR"
  exit 0
fi

echo "Draco files downloaded"
