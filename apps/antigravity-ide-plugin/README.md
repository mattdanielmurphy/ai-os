# Antigravity IDE Live Telemetry Plugin

Antigravity IDE status bar extension that bridges live token usage and triage mode telemetry from the local daemon into the IDE interface.

## Architecture

1. **Binary Shim** (`/Applications/Antigravity IDE.app/.../language_server_macos_arm`):
   - Intercepts language server arguments (`--workspace_id`, `--csrf_token`, etc.)
   - Dispatches non-blocking async preflight
   - Seamlessly proxies stdin/signals to `language_server_macos_arm.real`
   - Initializes `~/.hermes/antigravity_tokens.json`

2. **Telemetry Daemon** (`~/projects/ai-os/scripts/telemetry_daemon.py`):
   - Watches `~/.gemini/antigravity-ide/daemon/ls_*.log`
   - Real-time regex extraction for `prompt_tokens`, `completion_tokens`, and `[Triage]` routing
   - Performs atomic state updates to `~/.hermes/antigravity_tokens.json`

3. **Status Bar Extension Bridge** (`apps/antigravity-ide-plugin`):
   - Watches `~/.hermes/antigravity_tokens.json` at 500ms intervals
   - Displays `$(hubot) <promptTokens> in / <completionTokens> out | <triageMode>`
   - Detailed workspace and preflight metadata in status bar tooltip
