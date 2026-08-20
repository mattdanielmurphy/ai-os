# Restore Antigravity Native Language Server

**Date:** 2026-08-20  
**Scope:** Antigravity IDE language-server reliability

## Root cause

The Python binary shim installed as Antigravity's `language_server_macos_arm` read the complete stdin stream before passing it to the vendor binary, then closed the child stdin. Antigravity's language server is a persistent bidirectional stdio protocol, not a finite request stream. This behavior can deadlock initial handshakes and leave model requests stuck.

## Remediation

- Restored the original vendor Mach-O arm64 binary as the active `/Applications/Antigravity IDE.app/Contents/Resources/app/extensions/antigravity/bin/language_server_macos_arm`.
- Preserved the Python shim as `language_server_macos_arm.ai-os-shim.disabled` for forensic rollback only.
- Terminated the one live shim-managed server pair so the IDE may relaunch it through the restored native executable.

## Permanent safeguard

Antigravity IDE request handling is now explicitly native-only. AI-OS triage and telemetry may read logs or shared state, but must not wrap the language-server executable, buffer its streams, delay startup, alter its arguments, or route prompts away from Antigravity's cloud service.
