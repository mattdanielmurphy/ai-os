---
title: "Implement IPC Title Pattern"
date: "2026-08-17"
conversation_id: "f1463f46-2ed3-4279-a67e-e206b7ca44a0"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 17, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">In `/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/server.rs`:<br><br>1. In `handle_perplexity_query`:<br>In `sendDone(resp, err)`:<br>```javascript<br>            function sendDone(resp, err) {<br>                try {<br>                    function toB64(str) {<br>                        return btoa(unescape(encodeURIComponent(str || '')));<br>                    }<br>                    if (err) {<br>                        document.title = 'AIOS_ERROR_START:' + qId + ':' + toB64(err) + ':AIOS_ERROR_END';<br>                    } else {<br>                        document.title = 'AIOS_RESULT_START:' + qId + ':' + toB64(resp || '') + ':AIOS_RESULT_END';<br>                    }<br>                } catch(e) {}<br>```<br>And in the response loop in Rust:<br>```rust<br>    use base64::Engine;<br>    let start_time = std::time::Instant::now();<br>    let prefix_success = format!("AIOS_RESULT_START:{}:", query_id);<br>    let prefix_error = format!("AIOS_ERROR_START:{}:", query_id);<br><br>    loop {<br>        if start_time.elapsed() > std::time::Duration::from_secs(600) {<br>            let mut callbacks = get_query_callbacks().lock().await;<br>            callbacks.remove(&query_id);<br>            return Err((axum::http::StatusCode::GATEWAY_TIMEOUT, "Query timed out after 600 seconds".to_string()));<br>        }<br><br>        if let Ok(title) = win.title() {<br>            if title.starts_with(&prefix_success) {<br>                let rest = &title[prefix_success.len()..];<br>                if let Some(end_idx) = rest.rfind(":AIOS_RESULT_END") {<br>                    let b64_str = &rest[..end_idx];<br>                    let decoded_bytes = base64::engine::general_purpose::STANDARD.decode(b64_str).unwrap_or_default();<br>                    let decoded_str = String::from_utf8(decoded_bytes).unwrap_or_default();<br>                    let _ = win.set_title("Perplexity");<br>                    return Ok(Json(QueryResponse {<br>                        response: decoded_str,<br>                        query_id,<br>                    }));<br>                }<br>            } else if title.starts_with(&prefix_error) {<br>                let rest = &title[prefix_error.len()..];<br>                if let Some(end_idx) = rest.rfind(":AIOS_ERROR_END") {<br>                    let b64_str = &rest[..end_idx];<br>                    let decoded_bytes = base64::engine::general_purpose::STANDARD.decode(b64_str).unwrap_or_default();<br>                    let decoded_str = String::from_utf8(decoded_bytes).unwrap_or_default();<br>                    let _ = win.set_title("Perplexity");<br>                    return Err((axum::http::StatusCode::INTERNAL_SERVER_ERROR, format!("Perplexity execution error: {}", decoded_str)));<br>                }<br>            }<br>        }<br><br>        if let Ok(Ok(res)) = rx.try_recv() {<br>            let _ = win.set_title("Perplexity");<br>            return Ok(Json(QueryResponse {<br>                response: res,<br>                query_id,<br>            }));<br>        }<br><br>        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;<br>    }<br>```<br><br>2. Apply the exact same title-IPC pattern to `handle_gemini_query`.<br><br>3. In `handle_debug_ping` and `handle_debug_ping_gemini`:<br>Update script to set `document.title = 'AIOS_PING_RESULT:' + diag;` and poll `win.title()` in Rust for 5 seconds, returning `diag` when detected.</span>



<span title="Responded at 6:07am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The requested updates to `handle_perplexity_query`, `handle_gemini_query`, `handle_debug_ping`, and `handle_debug_ping_gemini` in `/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/server.rs` have been applied.

These handlers now use a `document.title`-based IPC pattern to communicate results or errors from the webview back to the Rust server. Specifically:

1.  The `sendDone` function in the injected JS now updates `document.title` with `AIOS_RESULT_START:...:AIOS_RESULT_END` or `AIOS_ERROR_START:...:AIOS_ERROR_END`, with the payload base64-encoded.
2.  The Rust code now polls `win.title()` to detect these prefixes and decode the results.
3.  Debug pings similarly use `AIOS_PING_RESULT:` in the title for identification and return.

I have messaged the parent agent confirming these changes.

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | Committed | PPLX Quota |
| :--- | :--- | :--- | :--- |
| ~40k / ~430k 🟢 (optimal) | 1:05am | 🟡 Uncommitted (1) | 94 ❓, 29 📤 |

<span style="position: absolute; right: 2rem; bottom: 0.5rem; display: inline-block; font-size: 11px; font-weight: 600; opacity: 0.7; padding: 3px 10px; border: 1px solid rgba(113,100,175,0.4); border-radius: 20px; white-space: nowrap; letter-spacing: 0.3px;"><a href="file:///Users/matt/.gemini/antigravity/brain/f1463f46-2ed3-4279-a67e-e206b7ca44a0/kanban.md" style="text-decoration:none;">📋 Kanban</a></span>

</span>

</span>