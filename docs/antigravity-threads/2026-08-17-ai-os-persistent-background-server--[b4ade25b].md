---
title: "AI-OS Persistent Background Server"
date: "2026-08-17"
conversation_id: "b4ade25b-6068-4ed1-984e-a93143d1be14"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 17, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">```[query_aios] ERROR: AI-OS is not running (http://127.0.0.1:3031 is unreachable).<br>Please open or start AI-OS manually:<br>  cd /Users/matt/projects/ai-os/apps/gemini-companion && bun tauri dev```<br>It IS running though! I can see it in my dock!<br>I've realized, this whole system is fucking stupid. We want a SERVER that is ALWAYS running, and will restart automatically if it crashes, that can handle these requests.<br>```<br></span>



<span title="Responded at 10:29pm" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

### Root Cause Identified & Resolved

1. **Why `http://127.0.0.1:3031` was unreachable despite the app appearing in Dock:**
   - In [`server.rs`](file:///Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/server.rs) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/server.rs) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/server.rs), the Axum TCP listener used `tokio::net::TcpListener::bind("127.0.0.1:3031").await.unwrap()`.
   - When launched while port `3031` was in `TIME_WAIT` or momentarily busy, Rust panicked with `AddrInUse`.
   - The Rust Tauri backend immediately crashed, while orphaned Vite processes or stale Dock references remained alive.
   - Vite also had `strictPort: true` on port `1420`, crashing on restart if a previous dev server had not fully exited.

---

### What Was Built & Fixed

1. **Crash-Proof Axum Server**:
   - Replaced `.unwrap()` with `tokio::net::TcpSocket` using `SO_REUSEADDR` and `SO_REUSEPORT`.
   - Added a 10-attempt backoff retry loop and non-panicking error recovery in [`server.rs`](file:///Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/server.rs) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/server.rs) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/server.rs).

2. **Always-Running Launch Agent (`la` managed)**:
   - Created `/Users/matt/Library/LaunchAgents/com.matt.agent.aios-server.plist` with `KeepAlive: true`, `RunAtLoad: true`, and `LimitLoadToSessionType: [Aqua, Background]`.
   - Supervised through `/Users/matt/Library/Scripts/tmux-agent-wrapper.sh` under named tmux session `agent-aios-server`.
   - Created [`run_aios_server.sh`](file:///Users/matt/projects/ai-os/scripts/run_aios_server.sh) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/run_aios_server.sh) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/run_aios_server.sh) with pre-launch cleanup for stale ports (`3031`, `1420`) and isolated ARM64 environment paths.
   - Added `aios-server` to `KNOWN_AGENTS` in [`~/.local/bin/la`](file:///Users/matt/.local/bin/la) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.local/bin/la) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.local/bin/la).

3. **Auto-Recovery in Client Scripts**:
   - Updated [`query_aios.js`](file:///Users/matt/projects/ai-os/scripts/query_aios.js) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/query_aios.js) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/query_aios.js) to automatically trigger `la start aios-server` and poll if the server is starting up or reloading, eliminating manual terminal start requirements.

---

### Management Commands

You can now inspect, restart, and tail the AI-OS server at any time using your standard `la` tool:

```bash
la status aios-server       # View status & running PID
la restart aios-server      # Restart server & webviews
tmux attach -t agent-aios-server  # Attach directly to the live server terminal
```

---

### Verification
- `curl http://127.0.0.1:3031/api/debug/ping` $\rightarrow$ `URL=https://www.perplexity.ai/ | PPLX=true | TAURI=true | WEBKIT=true` (0.01s).
- Direct query test: executed `node scripts/query_aios.js` $\rightarrow$ received response in **2.98s**.
- Planner test: executed `node scripts/query_aios.js --plan` $\rightarrow$ generated full implementation plan to `./tmp/planner_output.txt`.

---

- Active Backlog: [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)
- Conversation Log: [thread.md](file:///Users/matt/.gemini/antigravity/brain/b4ade25b-6068-4ed1-984e-a93143d1be14/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/b4ade25b-6068-4ed1-984e-a93143d1be14/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/b4ade25b-6068-4ed1-984e-a93143d1be14/thread.md)

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | Committed | PPLX Quota | Handoff |
| :--- | :--- | :--- | :--- | :--- |
| ~95k / ~450k 🟢 (optimal) | 5:30pm | 🟡 Uncommitted (3) | 79 ❓, 29 📤 | [⚡ -52% context · -16% cost T1](http://127.0.0.1:3031/handoff?session=b4ade25b-6068-4ed1-984e-a93143d1be14) |

<span style="position: absolute; right: 2rem; bottom: 0.5rem; display: inline-block; font-size: 11px; font-weight: 600; opacity: 0.7; padding: 3px 10px; border: 1px solid rgba(113,100,175,0.4); border-radius: 20px; white-space: nowrap; letter-spacing: 0.3px;"><a href="file:///Users/matt/.gemini/antigravity/brain/b4ade25b-6068-4ed1-984e-a93143d1be14/kanban.md" style="text-decoration:none;">📋 Kanban</a></span>

</span>

</span>