# AI-OS Always-On Companion Server Launch Agent Service

## Context
When running `query_aios.js`, requests failed with `[query_aios] ERROR: AI-OS is not running (http://127.0.0.1:3031 is unreachable)`.
Investigation revealed two critical failure modes:
1. **Port Bind Panics in Rust (`server.rs`)**: `TcpListener::bind("127.0.0.1:3031").await.unwrap()` panicked whenever port 3031 was in `TIME_WAIT` or temporarily held, immediately crashing the Tauri Rust backend and leaving orphaned Vite/node processes.
2. **Missing Always-On Daemon Supervision**: AI-OS had to be started manually in a terminal, with no `launchd` supervision to ensure 24/7 uptime and auto-restart on crash.
3. **Port 1420 Collision on Fast Restarts**: Vite failed with `Port 1420 is already in use`, terminating `tauri dev` on restart.

## Root Cause Fixes & Implementation
1. **Crash-Proof Axum Server (`apps/gemini-companion/src-tauri/src/server.rs`)**:
   - Replaced raw unwrapped binding with `tokio::net::TcpSocket` using `SO_REUSEADDR` and `SO_REUSEPORT`.
   - Added a 10-attempt backoff retry loop and graceful non-panicking error logging.
2. **Dedicated Launch Agent (`com.matt.agent.aios-server.plist`)**:
   - Created `/Users/matt/Library/LaunchAgents/com.matt.agent.aios-server.plist` configured with `KeepAlive: true`, `RunAtLoad: true`, and `LimitLoadToSessionType: [Aqua, Background]`.
   - Managed through `tmux-agent-wrapper.sh` under named tmux session `agent-aios-server`.
   - Created `/Users/matt/projects/ai-os/scripts/run_aios_server.sh` with automated port cleanup for 3031/1420 and clean ARM64 PATH.
3. **CLI Management Integration (`~/.local/bin/la`)**:
   - Added `aios-server` to `la`'s `KNOWN_AGENTS` for single-command management: `la list`, `la status aios-server`, `la restart aios-server`.
4. **Auto-Recovery in `scripts/query_aios.js`**:
   - When port 3031 is unreachable, `query_aios.js` automatically triggers `la restart aios-server` / `la start aios-server` and polls for up to 15 seconds before failing.

## Verification
- `la status aios-server` reports running with attached tmux session `agent-aios-server`.
- `curl http://127.0.0.1:3031/api/debug/ping` -> `URL=https://www.perplexity.ai/ | PPLX=true | TAURI=true | WEBKIT=true`.
- Executed end-to-end `query_aios.js` query: received final response in 2.98s.
- Executed `query_aios.js --plan`: generated full 5500-char implementation plan saved to `./tmp/planner_output.txt`.
