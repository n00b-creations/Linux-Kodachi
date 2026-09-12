Add rich GLTF dashboard model support, model-fetch helper, and integrate into installer.

- frontend/kdash/index.html: include GLTFLoader and DRACOLoader scripts
- frontend/kdash/app.js: attempt to load assets/models/dashboard_model.glb, fall back to remote sample, otherwise use cube
- frontend/kdash/assets/fetch_model.sh: helper to download a sample GLB into assets/models
- frontend/kdash/assets/README.md: instructions
- scripts/install-overlay.sh: call fetch_model.sh after copying frontend files
