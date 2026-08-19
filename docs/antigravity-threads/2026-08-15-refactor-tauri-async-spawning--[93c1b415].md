---
title: "Refactor Tauri Async Spawning"
date: "2026-08-15"
conversation_id: "93c1b415-9cbf-4e95-8da4-08236fbdd600"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 15, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">Please fix the async runtime spawning in `/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri`:

1. In `src/cloud_sync.rs`:
   - In `pub fn start_sync_scheduler(app_handle: tauri::AppHandle)`:
     Replace `tokio::spawn` with `tauri::async_runtime::spawn`.

2. In `src/proxy.rs`:
   - Add `pub fn spawn_proxy_server(app_handle: tauri::AppHandle)`:
```rust

pub fn spawn_proxy_server(app_handle: tauri::AppHandle) {
    tauri::async_runtime::spawn(async move {
        let _ = start_proxy_server(app_handle).await;
    });
}
```

3. In `src/main.rs`:
   - Change line 487 from:
     `tokio::spawn(proxy::start_proxy_server(app_handle.clone()));`
     to:
     `proxy::spawn_proxy_server(app_handle.clone());`

Report back when done.</span>



<span title="Responded at 9:33am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The requested async runtime spawning fixes have been implemented successfully in the following files:

*   [`/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/cloud_sync.rs`](file:///Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/cloud_sync.rs) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/cloud_sync.rs) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/cloud_sync.rs): Updated `start_sync_scheduler` to use `tauri::async_runtime::spawn`.
*   [`/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/proxy.rs`](file:///Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/proxy.rs) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/proxy.rs) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/proxy.rs): Added `spawn_proxy_server` function.
*   [`/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/main.rs`](file:///Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/main.rs) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/main.rs) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/main.rs): Updated the proxy server spawn call to use the new `proxy::spawn_proxy_server` function.

The caller agent has been notified.

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | PPLX Quota |
| :--- | :--- | :--- |
| ~35k / ~410k 🟢 (optimal) | 4:35am | 105 ❓, 16 📤 |

</span>

</span>