# Comprehensive Work Log: Fixing AI-OS Query Result Returning & Webview Multi-Channel IPC

## Issue Summary
`node scripts/query_aios.js` hung or timed out without returning the final response when queries were dispatched to the AI-OS companion webviews (`perplexity_main` and `gemini_main`).

## History & Root Cause Analysis of Previous Failures

### Why Past Attempts Failed:
1. **Remote Webview Tauri IPC Undefined**:
   - `apps/gemini-companion/src-tauri/src/server.rs` was relying on `window.__TAURI__.invoke('query_callback', ...)` and `window.__TAURI_INVOKE__`.
   - In WKWebView on macOS loading external remote domains (`https://www.perplexity.ai` and `https://gemini.google.com`), `window.__TAURI__` is **undefined** because Tauri's IPC injection is restricted on external origins without custom protocol injection.
2. **CORS & CSP Blocking HTTP Fetch Callbacks**:
   - Attempting `fetch('http://127.0.0.1:3031/api/perplexity/callback', { headers: { 'Content-Type': 'application/json' } })` failed because:
     - `Content-Type: application/json` triggers a CORS preflight `OPTIONS` request.
     - Perplexity's and Google's Content Security Policy (`connect-src`) blocks outgoing HTTP connections to `127.0.0.1`.
3. **Tauri IPC Envelope Error Parsing Collision**:
   - In Tauri 1.x's raw `InvokeMessage` deserializer, `error` at the top level is expected to be a `usize` (the error callback ID). When JavaScript passed `{ error: "some error message string" }`, Tauri dropped the message with `invalid type: string, expected usize`.
4. **`win.title()` vs `document.title` Desync**:
   - `win.title()` in Tao/Tauri reads `NSWindow.title`. Setting `document.title = ...` in WKWebView JavaScript updates `webView.title`, which does not propagate to `NSWindow.title` without native KVO binding.
5. **Perplexity 2.18 SSE Schema Migration**:
   - Perplexity transitioned its SSE streaming schema to `workflow_block` (`steps[...].items[...].payload.text_payload.text` / `chunks`). Legacy parsers expecting `parsed.answer` or `parsed.blocks[...].markdown_block.answer` returned empty strings on completed queries.

---

## Architectural Solutions Implemented

### 1. Robust Multi-Channel Zero-Failure IPC Return Bridge (`server.rs`)
Injected scripts now dispatch query completions across **5 redundant channels simultaneously**:
1. **`navigator.sendBeacon('http://127.0.0.1:3031/api/perplexity/callback', jsonStr)`**:
   - Uses browser's native background beacon.
2. **Simple Request Fetch (`mode: 'no-cors'`, `headers: { 'Content-Type': 'text/plain' }`)**:
   - Bypasses CORS preflight `OPTIONS` requests entirely.
3. **WebKit Message Handler IPC (`window.webkit.messageHandlers.ipc.postMessage`)**:
   - Sanitized envelope with `callback: 0, error: 0` (numbers) and `err_msg: ...` to avoid Tauri 1.x deserializer rejection.
4. **Zero-Network URL Hash Bridge (`location.hash = '#aios_res_<query_id>_<base64>'`)**:
   - Polled natively by Rust via `win.url().fragment()`. Completely zero-network and impervious to CSP, network rules, or CORS.
5. **Image Beacon Route (`new Image().src = 'http://127.0.0.1:3031/api/beacon?q=<id>&d=<base64>'`)**:
   - Handled by Axum with 1x1 transparent GIF response (allowed under permissive `img-src` policies).

### 2. Streamlined Axum Body Parsing & Beacon Endpoint
- `handle_perplexity_callback` updated to accept `axum::body::Bytes` so that raw plain-text payloads from `sendBeacon` and `no-cors` fetch are parsed seamlessly without rejecting on MIME type.
- Registered `/api/beacon` endpoint in Axum server.

### 3. Upgraded `perplexity-engine.js` Stream Parser
- Added recursive extraction for `workflow_block` (`steps -> items -> payload.text_payload`), `markdown_block`, direct string fields, and inner JSON text payloads.
- Preserved reasoning step streaming without premature termination until `parsed.final === true`, `parsed.text_completed === true`, or stream completion.

---

## Verification & Test Results
- `curl http://127.0.0.1:3031/api/debug/ping` -> `URL=https://www.perplexity.ai/ | PPLX=true | TAURI=true | WEBKIT=true` (0.01s response time).
- `curl http://127.0.0.1:3031/api/debug/ping_gemini` -> `URL=https://gemini.google.com/app | GEMINI=true | TAURI=true | WEBKIT=true` (0.01s response time).
- `node scripts/query_aios.js "Reply with the single word PONG and nothing else" --provider perplexity --model sonar` -> **Completed in 1.25s** with full output banner and exit code 0.
- `node scripts/query_aios.js "Reply with the single word PLANNER_OK and nothing else" --provider perplexity --model gemini` -> **Completed in 2.71s** with exit code 0.
- `node scripts/query_aios.js "Reply with the single word GEMINI_OK and nothing else" --provider gemini --model gemini-3.1-flash-lite` -> **Completed in 4.24s** with exit code 0.
