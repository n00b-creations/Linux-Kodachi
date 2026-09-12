# CYBER-OS Dashboard Integration

Phase 1B establishes the frontend boundary for K-Dash++.

The existing Kodachi 9 desktop/dashboard remains the host integration surface. CYBER-OS adds a separate application layer rather than replacing Kodachi-owned desktop files or services.

## Planned shell

- Tauri desktop shell
- Svelte UI
- Local CYBER-OS API
- Workspace-aware navigation
- Tool Registry-backed menus

## Initial workspaces

- Home
- Security
- Red Team
- Blue Team
- Purple Team
- OSINT
- DFIR
- AI
- Labs
- Reports
- Settings

This directory intentionally contains only the integration contract in Phase 1B; the production UI implementation will be added after the API and workspace contracts stabilize.
