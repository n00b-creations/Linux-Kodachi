---
*** Begin Patch
*** Update File: Kodachi-9/cyber-os-overlay/scripts/install-overlay.sh
@@
 if [ -d "$SRCDIR" ]; then
@@
   cp -a "$SRCDIR/integrations" "$PREFIX/" || true
   chmod -R 0755 "$PREFIX/scripts" || true
   find "$PREFIX/backend" -type f -name "*.py" -exec chmod 0644 {} + || true
 fi
@@
 fi
 
 # Attempt to fetch rich dashboard model if assets script exists
 if [ -x "$PREFIX/frontend/kdash/assets/fetch_model.sh" ]; then
   echo "Attempting to download dashboard model into $PREFIX/frontend/kdash/assets/models"
   "$PREFIX/frontend/kdash/assets/fetch_model.sh" "$PREFIX/frontend/kdash/assets/models" || true
 fi
+
+# Attempt to fetch a richer GLB model and DRACO decoders if present
+if [ -x "$PREFIX/frontend/kdash/assets/fetch_rich_model.sh" ]; then
+  echo "Attempting to download rich dashboard model into $PREFIX/frontend/kdash/assets/models"
+  "$PREFIX/frontend/kdash/assets/fetch_rich_model.sh" "$PREFIX/frontend/kdash/assets/models" || true
+fi
+if [ -x "$PREFIX/frontend/kdash/assets/fetch_draco.sh" ]; then
+  echo "Attempting to download DRACO decoders into $PREFIX/frontend/kdash/assets/draco"
+  "$PREFIX/frontend/kdash/assets/fetch_draco.sh" "$PREFIX/frontend/kdash/assets/draco" || true
+fi
*** End Patch
