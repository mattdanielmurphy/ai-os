---
title: "Apply Targeted Code Refactorings"
date: "2026-08-17"
conversation_id: "9551429c-96b6-4d40-82a5-2ef75ea6d883"
source: "antigravity"
---

# Apply Targeted Code Refactorings

## User

Please make the following targeted edits:

1. Target file: `/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/engines/perplexity-engine.js`
In `_parseStream(response)`:
Replace lines 179-183:
```javascript
                        if (parsed.status === 'completed' || parsed.status === 'success' || parsed.step_type === 'final' || parsed.final === true || parsed.text_completed === true) {
                            if (answer && answer.length > 0) {
                                isCompleted = true;
                                break;
                            }
                        }
```

2. Target file: `/Users/matt/projects/ai-os/scripts/query_aios.js`
- Remove all `setInterval` heartbeat logging and `clearInterval(heartbeat)` calls.
- In `main()`:
  Log a single concise startup line to `stderr`:
  `console.error(`[query_aios] Querying ${provider} via AI-OS (model: ${modelDisplay}, thread: ${sessionId}, timeout: ${timeoutSec}s)... (waiting for response)`);`
  And record `const startTime = Date.now();`
- When response arrives:
  Calculate `elapsed`, `chars`, `words`, `lines`.
  If `outputPath` is set:
  `fs.mkdirSync(path.dirname(path.resolve(outputPath)), { recursive: true });`
  `fs.writeFileSync(outputPath, answer, 'utf8');`
  `console.error(`[query_aios] ✅ Final output received (${chars} chars, ${elapsed}s) and saved to ${outputPath}`);`
  Print the clean completion banner to `stdout`:
  ```
  ================================================================================
  🎉 [AI-OS QUERY COMPLETE — FINAL OUTPUT RECEIVED]
  ================================================================================
  Provider: <provider>
  Model: <modelDisplay>
  Session / Thread ID: <sessionId>
  Elapsed time: <elapsed>s
  Character count: <chars>
  Word count: <words>
  Line count: <lines>
  Saved To: <outputPath or "N/A (stdout only)">
  --------------------------------------------------------------------------------
  <answer>
  ================================================
<truncated 825 bytes>
ws.onopen = function() {
                        ws.send(JSON.stringify(msgObj));
                        setTimeout(function() { ws.close(); }, 500);
                    };
                } catch(e) {}

                try {
                    if (window.__TAURI__ && window.__TAURI__.event) {
                        window.__TAURI__.event.emit('query_callback_event', msgObj);
                    }
                } catch (e) {}

                try {
                    if (window.__TAURI__ && window.__TAURI__.invoke) {
                        window.__TAURI__.invoke('query_callback', { queryId: qId, response: resp, errMsg: err, payload: msgObj }).catch(function() {});
                    }
                } catch (e) {}

                try {
                    if (window.__TAURI_INVOKE__) {
                        window.__TAURI_INVOKE__('query_callback', { queryId: qId, response: resp, errMsg: err, payload: msgObj });
                    }
                } catch (e) {}

                try {
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
                } catch (e) {}

                try {
                    fetch('http://127.0.0.1:3031/api/perplexity/callback', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query_id: qId, response: resp, error: err })
                    }).catch(function() {});
                } catch (e) {}
            }
```

---

## Assistant

All requested edits have been completed.

1.  **`/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/engines/perplexity-engine.js`**: Updated the `_parseStream` function to handle completion correctly without redundant checks.
2.  **`/Users/matt/projects/ai-os/scripts/query_aios.js`**: Removed heartbeat logging, updated startup logs to stderr, added elapsed time/word/line count calculations, and implemented the clean completion banner for stdout as requested.
3.  **`/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/server.rs`**: Updated `sendDone` functions within `handle_perplexity_query` and `handle_gemini_query` to use the standardized `msgObj` and clean parameters to prevent Tauri IPC collisions.

---
