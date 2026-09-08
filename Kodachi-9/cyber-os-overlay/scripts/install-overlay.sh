@@
 SRCDIR="$(pwd)/Kodachi-9/cyber-os-overlay"
 if [ -d "$SRCDIR" ]; then
   cp -a "$SRCDIR/backend" "$PREFIX/" || true
   cp -a "$SRCDIR/scripts" "$PREFIX/" || true
-  cp -a "$SRCDIR/frontend" "$PREFIX/" || true
+  cp -a "$SRCDIR/frontend" "$PREFIX/" || true
   cp -a "$SRCDIR/integrations" "$PREFIX/" || true
   chmod -R 0755 "$PREFIX/scripts" || true
   find "$PREFIX/backend" -type f -name "*.py" -exec chmod 0644 {} + || true
 fi
@@
 else
   echo "systemctl not found; skipping systemd install"
 fi
+
+# Attempt to fetch rich dashboard model if assets script exists
+if [ -x "$PREFIX/frontend/kdash/assets/fetch_model.sh" ]; then
+  echo "Attempting to download dashboard model into $PREFIX/frontend/kdash/assets/models"
+  "$PREFIX/frontend/kdash/assets/fetch_model.sh" "$PREFIX/frontend/kdash/assets/models" || true
+fi
