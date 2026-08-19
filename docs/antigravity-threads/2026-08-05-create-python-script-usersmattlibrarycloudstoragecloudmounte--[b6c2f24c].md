---
title: "Create python script `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/scripts/photon_notify.py` (which syncs via SFTP to `/home/ubuntu/projects/jules-burner/scripts/photon_notify.py` on the VPS)."
date: "2026-08-05"
conversation_id: "b6c2f24c-3bcf-4ec1-b31b-6e28c7ad4229"
source: "antigravity"
---

# Create python script `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/scripts/photon_notify.py` (which syncs via SFTP to `/home/ubuntu/projects/jules-burner/scripts/photon_notify.py` on the VPS).

## User

Create python script `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/scripts/photon_notify.py` (which syncs via SFTP to `/home/ubuntu/projects/jules-burner/scripts/photon_notify.py` on the VPS).

Requirements:
1. Standard Python executable script (`#!/usr/bin/env python3`).
2. Read env vars:
   - PHOTON_PROJECT_ID: `f8db2b93-77ed-4efc-824c-7771891440e2` (default fallback if not in env)
   - PHOTON_PROJECT_SECRET: `HIZBy7MsKCXyoI6DJ34iUrdQe-ZHgNjBfS8XzsiXtCk` (default fallback if not in env)
   - PHOTON_PHONE_NUMBER / PHOTON_HOME_CHANNEL: `+18259775250`
3. Also attempt to load `/home/ubuntu/.hermes/.env` or `/home/ubuntu/projects/jules-burner/.env` if present.
4. To send the message on the VPS, execute a Node script using `node` or `bun` with `spectrum-ts` or standard HTTP request if spectrum-ts sidecar is installed, OR execute an inline node script targeting `/home/ubuntu/.hermes/hermes-agent/plugins/platforms/photon/sidecar` if available, or call Spectrum SDK.
Let's check if `/home/ubuntu/.hermes/hermes-agent/plugins/platforms/photon/sidecar` exists on VPS or if node module `spectrum-ts` exists on VPS.

Write out `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/scripts/photon_notify.py` using `write_to_file`. Make sure `chmod +x` equivalent permissions.

---
