---
title: "Project Engine Proxy Setup"
date: "2026-08-15"
conversation_id: "bef1da44-57b5-42a3-b164-0c177a4e2ae4"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 15, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 80px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Please perform the following file creation and edits in /Users/matt/projects/ai-os:

1. Create directory `/Users/matt/projects/ai-os/tauri-gui/src-tauri/engines` if it doesn't exist.
2. Read the source engine `/Users/matt/projects/external/Proxima/electron/providers/engines/perplexity-engine.js` and copy/save it as `/Users/matt/projects/ai-os/tauri-gui/src-tauri/engines/perplexity-engine.js`.
3. Read the source engine `/Users/matt/projects/external/Proxima/electron/providers/engines/gemini-engine.js` and copy/save it as `/Users/matt/projects/ai-os/tauri-gui/src-tauri/engines/gemini-engine.js`.
4. In both engine files, ensure any telemetry/save callbacks send thread data via fetch to `http://127.0.0.1:19223/api/thread/save` (using port 19223 to avoid conflicts with Proxima on 19222).
5. Create `/Users/matt/projects/ai-os/tauri-gui/src-tauri/src/proxy.rs`:
   - An Axum HTTP server running on port 19223 (`127.0.0.1:19223`).
   - Routes:
     - `GET /api/status` -> returns `{"status": "ok", "port": 19223, "version": "proxima-lite-0.1.0"}`
     - `POST /api/thread/save` -> receives JSON with `provider`, `thread_id`, `title`, `messages`, formats to Markdown, hashes SHA-256 to avoid redundant disk writes, and writes atomically to `~/projects/ai-os/context/threads/<provider>_<thread_id>.md`.
   - Setup CORS allowing `*` or `https://gemini.google.com` and `https://www.perplexity.ai`.
   - Export `pub async fn start_proxy_server(app_handle: tauri::AppHandle)` or similar starter function.
6. Edit `/Users/matt/projects/ai-os/tauri-gui/src-tauri/src/main.rs`:
   - Add `mod proxy;` at the top.
   - In `main()` or the Tauri setup hook, spawn `tokio::spawn(proxy::start_proxy_server(...));` so the port 19223 proxy starts automatically when Tauri starts.
   - Add `include_str!("../engines/gemini-engine.js")` and `include_str!("../engines/perplexity-engine.js")` into the webview initialization scripts if not already present.

Report back when all files have been written and edited.

</span>



<span title="Responded at 8:05am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

*(response in progress or not recorded)*

</span>



</span>

</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">



**Thread Metrics:**

| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~33k | 3:05am | ~33k / ~403k 🟢 (optimal) | 108, 20 🔬, 16 📤 |

</span>