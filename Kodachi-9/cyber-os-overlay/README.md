# Minimal README for the cyber-os-overlay module

This directory contains the CYBER-OS Overlay Phase 1 prototype.

Quick start (developer/testing):

1. Install Python dependencies:
   pip3 install -r Kodachi-9/cyber-os-overlay/requirements.txt

2. Run the API for testing (non-root):
   cd Kodachi-9/cyber-os-overlay
   python3 -m uvicorn backend.cyber_os_api:app --host 127.0.0.1 --port 8765

   Non-root runs write logs under XDG_STATE_HOME/cyber-os/log, or under
   ~/.local/state/cyber-os/log when XDG_STATE_HOME is unset. Root runs default
   to /var/log/cyber-os; CYBER_OS_LOG_DIR overrides either default.

3. Start the dashboard static server (optional):
   cd frontend/kdash
   python3 -m http.server 8000

For a system-wide install on a Debian-family host, run:
   sudo Kodachi-9/cyber-os-overlay/scripts/install-overlay.sh

The installer copies the overlay into /opt/cyber-os by default and creates the
CYBER-OS desktop entry. It does not enable or start the systemd service.
Set CYBER_OS_PREFIX, CYBER_OS_CONFIG, CYBER_OS_STATE, CYBER_OS_LOG, or
CYBER_OS_DESKTOP to override the corresponding install destinations.
