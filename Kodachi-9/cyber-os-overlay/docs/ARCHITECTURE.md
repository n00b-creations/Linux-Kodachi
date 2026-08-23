# CYBER-OS Overlay Architecture

## Boundary model

```text
+-----------------------------------------------------------+
|                    Kodachi 9 / Debian                     |
|                                                           |
|  Existing services  Existing dashboard  Existing tools    |
|          ^                 ^                 ^             |
|          |                 |                 |             |
|  --------+-----------------+-----------------+----------   |
|                         Overlay boundary                  |
|                                                           |
|  /opt/cyber-os                                            |
|    backend        local API and discovery                 |
|    plugins        plugin manifests                        |
|    integrations   tool-source adapters                    |
|    config         application defaults                    |
|    scripts        lifecycle utilities                    |
+-----------------------------------------------------------+
```

## Ownership rules

CYBER-OS owns only its overlay paths and its desktop launcher. It must not silently replace Kodachi binaries, services, desktop configuration, package metadata, or security controls.

## Tool registry

A tool is represented by metadata rather than by copied application-menu files. This lets the dashboard present Kodachi, BlackArch, Kali, forensic, and custom tools through a common UI while preserving their original installation ownership.

## Plugin model

Plugins declare an API version, identity, UI location, and permissions. Phase 1 does not execute plugin code automatically. Execution permissions will be added only after a signed-plugin and capability model is implemented.

## AI boundary

AI is disabled in the Phase 1 default configuration. Later phases may add local model providers and workflow orchestration, but tool execution must remain explicitly authorized, auditable, and constrained to configured environments.

## Lab boundary

Virtual-machine and container orchestration are future modules. Phase 1 contains no network attack automation and no remote execution service.
