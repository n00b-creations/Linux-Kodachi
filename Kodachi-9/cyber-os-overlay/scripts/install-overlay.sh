---
*** Begin Patch
*** Update File: Kodachi-9/cyber-os-overlay/scripts/install-overlay.sh
@@
   cp -a "$SRCDIR/frontend" "$PREFIX/" || true
   cp -a "$SRCDIR/integrations" "$PREFIX/" || true
+  # copy default node map mapping config into frontend (if present)
+  if [ -f "$SRCDIR/frontend/kdash/config/node_map.yaml" ]; then
+    install -m 0644 "$SRCDIR/frontend/kdash/config/node_map.yaml" "$PREFIX/frontend/kdash/config/node_map.yaml" || true
+  fi
   chmod -R 0755 "$PREFIX/scripts" || true
   find "$PREFIX/backend" -type f -name "*.py" -exec chmod 0644 {} + || true
 fi
*** End Patch
