---
title: "Optimize AI-OS Query Processing"
date: "2026-08-17"
conversation_id: "dbdd6261-21f9-4d8a-b9f9-f7f377abd74a"
source: "antigravity"
---

# Optimize AI-OS Query Processing

## User

Please make the following file edits to improve AI-OS query completion signaling, fix the Perplexity stream parsing, and ensure robust IPC and timeout handling:

1. Target file: `/Users/matt/projects/ai-os/scripts/query_aios.js`
- Add a periodic heartbeat timer (every 4 seconds) using `setInterval` that logs progress to `stderr`: `[query_aios] [Xs] Generating response via <provider> (<modelDisplay>)...`
- When the query response arrives, clear the heartbeat timer.
- Calculate elapsed seconds, character count, word count, line count.
- If `outputPath` is specified, write the clean `answer` string to `outputPath` and log `[query_aios] ✅ Final output received (<chars> chars, <time>s) and saved to <outputPath>` to `stderr`.
- Print a clear, prominent completion banner to `stdout` containing:
  - Header: `================================================================================`
  - Title: `🎉 [AI-OS QUERY COMPLETE — FINAL OUTPUT RECEIVED]`
  - Metadata: Provider, Model, Session / Thread ID, Elapsed time, Character / Word / Line counts, Saved To path
  - Separator
  - Full output text (`answer`)
  - Footer: `🏁 [END OF AI-OS FINAL OUTPUT]`
  - End separator

2. Target file: `/Users/matt/projects/ai-os/scripts/pplx_quota.py`
- In `get_pplx_quota(force=False)`: Ensure `cookie_header = get_pplx_cookies()` is called before `if not cookie_header:`.

3. Target file: `/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/engines/perplexity-engine.js`
- In `_parseStream(response)`: Fix premature loop termination. Do NOT break on intermediate search step statuses. Only set `isCompleted = true` if `data === '[DONE]'` or if `(parsed.text_completed === true || parsed.final === true) && answer.length > 0`.

4. Target file: `/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/server.rs`
- In `handle_perplexity_query`: Increase timeout from 180s to 600s (`Duration::from_secs(600)`). Update timeout error message to 600 seconds.
- In `handle_gemini_query`: Increase timeout from 180s to 600s (`Duration::from_secs(600)`). Update timeout error message to 600 seconds.
- In `sendDone` inside `handle_perplexity_query`, `handle_gemini_query`, `handle_debug_ping`, `handle_debug_ping_gemini`:
  Ensure the Tauri invoke and webkit postMessage payload format is clean:
  ```javascript
  if (window.__TAURI__ && window.__TAURI__.invoke) {
      window.__TAURI__.invoke('query_callback', { queryId: qId, response: resp, errMsg: err }).catch(function() {});
  }
  if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.ipc) {
      window.webkit.messageHandlers.ipc.postMessage({
          cmd: 'query_callback',
          callback: 0,
          error: 0,
          queryId: qId,
          response: resp,
          errMsg: err
      });
  }
  ```

5. Target file: `/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/main.rs`
- In `query_callback`: Accept `err_msg: Option<String>` and `query_id: Option<String>` and handle alias so it never fails deserialization from camelCase or snake_case:
  ```rust
  #[tauri::command]
  async fn query_callback(
      query_id: Option<String>,
      response: Option<String>,
      error: Option<String>,
      err_msg: Option<String>,
      payload: Option<QueryCallbackPayload>,
  ) -> Result<(), String>
  ```
  Check `err_msg` in `let err = error.or(err_msg)...`

6. Target file: `/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/tauri.conf.json`
- In `windows` array, add `gemini_main`, `perplexity_main`, and `floating`.
- In `allowlist`, set `"all": true`.
- In `dangerousRemoteDomainIpcAccess`, include `gemini_main`, `perplexity_main`, `floating`, `main` for `gemini.google.com`, `www.perplexity.ai`, `perplexity.ai`.

---

## Assistant

The requested file edits have been successfully applied:

*   **`/Users/matt/projects/ai-os/scripts/query_aios.js`**: Implemented a 4-second heartbeat timer that logs progress to `stderr`, updated the response handler to calculate performance metrics (elapsed time, character/word/line counts), implemented clean file output, and added the final completion banner to `stdout`.
*   **`/Users/matt/projects/ai-os/scripts/pplx_quota.py`**: Fixed `get_pplx_quota` to ensure `get_pplx_cookies()` is called to initialize `cookie_header` before the validation check.
*   **`/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/engines/perplexity-engine.js`**: Refactored `_parseStream` to avoid breaking the stream prematurely, ensuring it only completes correctly when `[DONE]` or a final result is received.
*   **`/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/server.rs`**: Increased timeouts from 180s to 600s for both Perplexity and Gemini queries and updated the JavaScript logic in `sendDone` to ensure clean, consistent IPC payload structures.
*   **`/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/main.rs`**: Updated `query_callback` to accept `err_msg` and `query_id` parameters, with robust deserialization and proper error propagation.
*   **`/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/tauri.conf.json`**: Configured the required additional windows (`gemini_main`, `perplexity_main`, `floating`), enabled `all: true` in the allowlist, and updated the `dangerousRemoteDomainIpcAccess` policy to allow cross-window IPC access for the required domains.

---
