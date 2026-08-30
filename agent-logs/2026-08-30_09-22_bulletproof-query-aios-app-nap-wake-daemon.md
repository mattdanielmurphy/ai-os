# Engineering Log: Hardened AI-OS Companion App, App Nap Elimination & Webview Wake Protocol

**Date:** 2026-08-30  
**Context:** `query_aios.js` and AI-OS Companion App (`apps/gemini-companion`)  
**Objective:** Make `query_aios.js` and the underlying AI-OS companion webviews (Perplexity & Gemini) 100% reliable, eliminating App Nap, background suspension, and sleep issues.

## Root Cause Analysis
1. **macOS App Nap & WebProcess Suspension:** When the Tauri app (`apps/gemini-companion`) ran in the background without user interaction, macOS App Nap throttled and suspended JavaScript execution, event loops, and network timers in WKWebView (`perplexity_main` and `gemini_main`).
2. **Window Destruction on Close:** When a user closed a companion window (Cmd+W or red (X) button), Tauri destroyed the `tauri::Window` instance by default. Subsequent queries failed with `NOT_FOUND: Gemini main window not found` or `Perplexity main window not found`.
3. **Absence of Webview Keepalive & Wake Protocol:** Background webviews occluded or hidden for extended periods would enter WebKit sleep without a heartbeat, causing HTTP/eval queries to time out. `query_aios.js` previously only verified `/v1/models` without ensuring the webview itself was awake and ready.

## Key Changes
1. **Eliminated App Nap Permanently (`main.rs` & `run_aios_server.sh`):**
   - Implemented `disable_app_nap()` using Cocoa `NSProcessInfo` `beginActivityWithOptions:` with `NSActivityUserInitiated | NSActivityLatencyCritical | NSActivityIdleSystemSleepDisabled | NSActivityAutomaticTerminationDisabled` on startup.
   - Wrapped the companion app runner in `caffeinate -s -i bun tauri dev` in `scripts/run_aios_server.sh`.
2. **Window Destruction Prevention & On-Demand Recreation (`main.rs` & `server.rs`):**
   - Registered `.on_window_event(...)` to intercept `tauri::WindowEvent::CloseRequested`, calling `api.prevent_close()` and `window.hide()` to preserve window memory and state.
   - Added `create_gemini_window` and `create_perplexity_window` builders in `main.rs`.
   - Implemented `ensure_perplexity_window` and `ensure_gemini_window` in `server.rs` to dynamically re-spawn and initialize windows if they are ever missing.
3. **Automated URL Verification & Wake Heartbeat (`server.rs`):**
   - Added webview URL checks prior to executing queries, auto-navigating to `https://www.perplexity.ai` or `https://gemini.google.com/app` if the webview crashed or navigated away.
   - Added a 15-second tokio background keepalive heartbeat to touch both webviews (`window.__aiosKeepalive = Date.now()`), preventing WebKit idle garbage collection and WebProcess suspension.
   - Added `/api/wake` (POST/GET) and `/api/health` (GET) endpoints.
4. **Client-Side Proactive Wake Protocol (`query_aios.js`):**
   - Implemented `wakeAios(baseUrl, provider)` in `query_aios.js` to proactively check and wake the server and target provider webview before dispatching queries, automatically managing `la restart aios-server` if needed.

## Verification
- Verified `cargo check` and full Tauri app build with Cocoa/ObjC integration.
- Verified `/api/health`, `/api/wake`, `/api/debug/ping`, and `/api/debug/ping_gemini` returned active online states.
- Tested `node scripts/query_aios.js "Reply with the single word PONG if you receive this." --provider perplexity --model sonar` — received "PONG" in 1.67 seconds.
