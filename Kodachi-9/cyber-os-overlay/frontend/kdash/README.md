# K-Dash++ Phase 1C

K-Dash++ is the CYBER-OS overlay dashboard shell. It consumes the local CYBER-OS API and provides workspace navigation without replacing Kodachi-owned desktop services.

## Run during development

Serve this directory with any static HTTP server, then start the CYBER-OS API on localhost port 8765.

The dashboard is intentionally read-only in Phase 1C. It does not execute arbitrary commands, install tools, or modify the host.

## Workspaces

Home, Security, Red Team, Blue Team, Purple Team, OSINT, DFIR, AI, Labs, Reports, and Settings are established as navigation boundaries. Providers will be connected incrementally through the Tool Registry and workflow APIs.
