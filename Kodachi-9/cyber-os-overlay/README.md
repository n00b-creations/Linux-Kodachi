# CYBER-OS Overlay — Phase 1

CYBER-OS is a non-destructive operations layer for Kodachi 9. It is intentionally separated from Kodachi-owned system files so the platform can evolve independently and remain removable.

## Design principles

- Kodachi remains the operating-system foundation.
- CYBER-OS installs under `/opt/cyber-os`.
- Persistent configuration belongs under `/etc/cyber-os`.
- Runtime state belongs under `/var/lib/cyber-os`.
- Logs belong under `/var/log/cyber-os`.
- Desktop integration is limited to a `.desktop` launcher and CYBER-OS-owned assets.
- Existing Kodachi services and applications are discovered, not replaced.
- Tool integrations use a registry/plugin model rather than copying another distribution's desktop files into Kodachi.
- The first release is intended for defensive operations, security education, isolated labs, and authorized testing.

## Phase 1 scope

1. Overlay directory layout.
2. Kodachi environment detection.
3. Tool discovery registry.
4. Plugin manifest format.
5. Minimal local API service.
6. Dashboard launcher integration.
7. Configuration and logging foundations.
8. Install and uninstall/rollback scripts.

## Planned directories

```text
cyber-os-overlay/
├── backend/       API and discovery services
├── config/        default configuration and schemas
├── integrations/  Kodachi and future tool-source adapters
├── plugins/       plugin manifests
├── scripts/       install, uninstall, health-check utilities
├── dashboard/     dashboard shell assets
└── docs/          architecture documentation
```

## Runtime layout

```text
/opt/cyber-os/
/etc/cyber-os/
/var/lib/cyber-os/
/var/log/cyber-os/
/usr/share/applications/cyber-os.desktop
```

No Phase 1 script should overwrite files owned by Kodachi. Future integration changes must be explicit, reversible, and tested independently.
