# Minimal README for the cyber-os-overlay module

This directory contains the CYBER-OS Overlay Phase 1 prototype.

Quick start (developer/testing):

1. Install Python deps:
   pip3 install -r Kodachi-9/cyber-os-overlay/requirements.txt

2. Run API for testing (non-root):
   cd Kodachi-9/cyber-os-overlay
   python3 -m uvicorn backend.cyber_os_api:app --host 127.0.0.1 --port 8765

3. Start dashboard static server (optional):
   cd frontend/kdash
   python3 -m http.server 8000

Files added:
- backend/cyber_os_api.py
- backend/tool_registry.py
- integrations/tool-registry/providers/kodachi.yaml
- scripts/run-cyber-os.sh
- scripts/systemd/cyber-os-api.service
- scripts/install-overlay.sh
- requirements.txt
- tests/test_api.py
