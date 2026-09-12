Updated KDASH frontend with 3D cube visualization and live API integration.

- Added frontend/kdash/index.html, style.css, app.js
- 3D visuals use Three.js (via CDN). The cube shows workspace faces and animates.
- Dashboard now fetches /health and /tools from the local API and displays tool availability.
- Controls: refresh tools, check health, toggle rotation, workspace buttons.

Notes:
- The dashboard expects the API at http://127.0.0.1:8765. If you run API on a different host/port, update API_BASE in app.js or serve a proxy.
- To preview locally, run: python3 -m http.server 8000 from the frontend/kdash directory and open http://localhost:8000
