use axum::{
    routing::post,
    Router,
    Json,
    extract::State as AxumState,
    extract::ws::{Message, WebSocket, WebSocketUpgrade},
};
use tower_http::cors::{CorsLayer, Any};
use futures_util::{SinkExt, StreamExt};
use tokio::sync::mpsc;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::collections::HashMap;
use tauri::Manager;

use crate::types::{
    ContextSyncPayload, CommitPayload, GeminiSyncPayload,
    RevisionEvent,
};

// ---------------------------------------------------------------------------
// WebSocket state
// ---------------------------------------------------------------------------

struct WsState {
    host_tx: Option<(u64, mpsc::UnboundedSender<Message>)>,
    clients: HashMap<String, mpsc::UnboundedSender<Message>>,
}

static WS_STATE: std::sync::OnceLock<std::sync::Mutex<WsState>> =
    std::sync::OnceLock::new();
static CLIENT_ID_COUNTER: AtomicU64 = AtomicU64::new(1);

fn get_ws_state() -> &'static std::sync::Mutex<WsState> {
    WS_STATE.get_or_init(|| {
        std::sync::Mutex::new(WsState {
            host_tx: None,
            clients: HashMap::new(),
        })
    })
}

// ---------------------------------------------------------------------------
// HTTP handlers
// ---------------------------------------------------------------------------

async fn handle_sync(
    Json(payload): Json<ContextSyncPayload>,
) -> Result<String, (axum::http::StatusCode, String)> {
    let project_root = std::env::var("AIOS_INITIAL_PROJECT").unwrap_or_else(|_| {
        let cwd = std::env::current_dir().unwrap();
        if cwd.ends_with("src-tauri") {
            cwd.parent().unwrap().to_string_lossy().to_string()
        } else {
            cwd.to_string_lossy().to_string()
        }
    });

    println!(
        "Received sync payload for thread {} in root {}",
        payload.thread_id, project_root
    );

    let log_dir = std::path::Path::new(&project_root)
        .join("gemini-history")
        .join("threads");

    std::fs::create_dir_all(&log_dir)
        .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let file_path = log_dir.join(format!("{}.md", payload.thread_id));

    std::fs::write(&file_path, &payload.content)
        .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok("Sync OK".to_string())
}

async fn handle_commit(
    AxumState(app_handle): AxumState<tauri::AppHandle>,
    Json(payload): Json<CommitPayload>,
) -> Result<String, (axum::http::StatusCode, String)> {
    let project_root = std::env::var("AIOS_INITIAL_PROJECT")
        .unwrap_or_else(|_| std::env::current_dir().unwrap().to_string_lossy().to_string());

    let log_dir = std::path::Path::new(&project_root)
        .join("agent-logs")
        .join("git")
        .join(&payload.thread_uuid);

    std::fs::create_dir_all(&log_dir)
        .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    if !log_dir.join(".git").exists() {
        std::process::Command::new("git")
            .current_dir(&log_dir)
            .arg("init")
            .output()
            .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;
    }

    let target_path = log_dir.join(&payload.target_filename);
    std::fs::write(&target_path, &payload.content)
        .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    std::process::Command::new("git")
        .current_dir(&log_dir)
        .arg("add")
        .arg(&payload.target_filename)
        .output()
        .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    std::process::Command::new("git")
        .current_dir(&log_dir)
        .arg("commit")
        .arg("--allow-empty")
        .arg("-m")
        .arg("Web Sync")
        .output()
        .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let output = std::process::Command::new("git")
        .current_dir(&log_dir)
        .arg("rev-parse")
        .arg("HEAD")
        .output()
        .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let commit_hash = String::from_utf8_lossy(&output.stdout).trim().to_string();

    app_handle
        .emit_all(
            "revision-commit",
            RevisionEvent {
                thread_uuid: payload.thread_uuid,
                target_filename: payload.target_filename,
                commit_hash,
            },
        )
        .ok();

    Ok("Commit OK".to_string())
}

async fn handle_gemini_sync(
    Json(payload): Json<GeminiSyncPayload>,
) -> Result<String, (axum::http::StatusCode, String)> {
    let project_root = std::env::var("AIOS_INITIAL_PROJECT").unwrap_or_else(|_| {
        let cwd = std::env::current_dir().unwrap();
        if cwd.ends_with("src-tauri") {
            cwd.parent().unwrap().to_string_lossy().to_string()
        } else {
            cwd.to_string_lossy().to_string()
        }
    });

    println!(
        "Received gemini sync payload for url {} in root {}",
        payload.url, project_root
    );

    let log_dir = std::path::Path::new(&project_root)
        .join("gemini-history")
        .join("userscript_logs");

    std::fs::create_dir_all(&log_dir)
        .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let timestamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_millis();
    let file_path = log_dir.join(format!("gemini_sync_{}.json", timestamp));

    let content = serde_json::json!({
        "timestamp": timestamp,
        "url": payload.url,
        "body": payload.body
    });

    std::fs::write(
        &file_path,
        serde_json::to_string_pretty(&content).unwrap(),
    )
    .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok("Sync OK".to_string())
}

// ---------------------------------------------------------------------------
// WebSocket handler
// ---------------------------------------------------------------------------

async fn ws_handler(ws: WebSocketUpgrade) -> impl axum::response::IntoResponse {
    ws.on_upgrade(handle_socket)
}

async fn handle_socket(socket: WebSocket) {
    let (mut sender, mut receiver) = socket.split();
    let (tx, mut rx) = mpsc::unbounded_channel::<Message>();

    let conn_id = CLIENT_ID_COUNTER.fetch_add(1, Ordering::SeqCst);
    let my_client_id = format!("client_{}", conn_id);
    let client_id_clone = my_client_id.clone();

    let write_task = tokio::spawn(async move {
        while let Some(msg) = rx.recv().await {
            if sender.send(msg).await.is_err() {
                break;
            }
        }
    });

    let mut registered_role = None;

    while let Some(Ok(msg)) = receiver.next().await {
        if let Message::Text(text) = msg {
            if let Ok(val) = serde_json::from_str::<serde_json::Value>(&text) {
                if let Some(msg_type) = val["type"].as_str() {
                    match msg_type {
                        "register" => {
                            let role = val["role"].as_str().unwrap_or("");
                            if role == "host" {
                                registered_role = Some("host");
                                let mut state = get_ws_state().lock().unwrap();
                                state.host_tx = Some((conn_id, tx.clone()));
                            } else if role == "client" {
                                registered_role = Some("client");
                                let mut state = get_ws_state().lock().unwrap();
                                state.clients
                                    .insert(my_client_id.clone(), tx.clone());
                            }
                        }
                        "query_callback" => {
                            let q_id = val["query_id"]
                                .as_str()
                                .or_else(|| val["queryId"].as_str())
                                .unwrap_or("")
                                .to_string();
                            let resp = val["response"].as_str().map(|s| s.to_string());
                            let err = val["error"].as_str().map(|s| s.to_string());
                            tokio::spawn(async move {
                                resolve_query_callback(&q_id, resp, err).await;
                            });
                        }
                        "invoke" => {
                            let mut payload = val.clone();
                            payload["client_id"] = serde_json::Value::String(
                                my_client_id.clone(),
                            );
                            let forward_msg =
                                Message::Text(payload.to_string().into());
                            let state = get_ws_state().lock().unwrap();
                            if let Some((_, host_tx)) = &state.host_tx {
                                let _ = host_tx.send(forward_msg);
                            }
                        }
                        "invoke_result" => {
                            if let Some(target_client_id) =
                                val["client_id"].as_str()
                            {
                                let state = get_ws_state().lock().unwrap();
                                if let Some(client_tx) =
                                    state.clients.get(target_client_id)
                                {
                                    let _ = client_tx
                                        .send(Message::Text(val.to_string().into()));
                                }
                            }
                        }
                        "event" => {
                            let state = get_ws_state().lock().unwrap();
                            let msg_text = val.to_string();
                            for client_tx in state.clients.values() {
                                let _ = client_tx.send(Message::Text(
                                    msg_text.clone().into(),
                                ));
                            }
                        }
                        _ => {}
                    }
                }
            }
        }
    }

    let mut state = get_ws_state().lock().unwrap();
    if let Some(role) = registered_role {
        if role == "host" {
            if let Some((existing_id, _)) = &state.host_tx {
                if *existing_id == conn_id {
                    state.host_tx = None;
                }
            }
        } else {
            state.clients.remove(&client_id_clone);
        }
    }
    write_task.abort();
}

#[derive(serde::Deserialize)]
pub struct PromptDispatchPayload {
    pub prompt: String,
    pub model: Option<String>,
    pub session_id: Option<String>,
}

#[derive(serde::Deserialize)]
pub struct PerplexityCallbackPayload {
    pub query_id: String,
    pub response: Option<String>,
    pub error: Option<String>,
}

type QueryCallbackMap = Arc<tokio::sync::Mutex<HashMap<String, tokio::sync::oneshot::Sender<Result<String, String>>>>>;

static QUERY_CALLBACKS: std::sync::OnceLock<QueryCallbackMap> = std::sync::OnceLock::new();

pub fn get_query_callbacks() -> &'static QueryCallbackMap {
    QUERY_CALLBACKS.get_or_init(|| {
        Arc::new(tokio::sync::Mutex::new(HashMap::new()))
    })
}

pub async fn resolve_query_callback(
    q_id: &str,
    resp: Option<String>,
    err: Option<String>,
) -> bool {
    eprintln!("[RESOLVE_QUERY_CALLBACK] q_id={}, resp_len={:?}, err={:?}", q_id, resp.as_ref().map(|s| s.len()), err);
    let mut callbacks = get_query_callbacks().lock().await;
    if let Some(tx) = callbacks.remove(q_id) {
        if let Some(e) = err {
            let _ = tx.send(Err(e));
        } else {
            let _ = tx.send(Ok(resp.unwrap_or_default()));
        }
        true
    } else {
        eprintln!("[RESOLVE_QUERY_CALLBACK NOT FOUND] q_id={}", q_id);
        false
    }
}

async fn handle_prompt_dispatch(
    AxumState(app_handle): AxumState<tauri::AppHandle>,
    Json(payload): Json<PromptDispatchPayload>,
) -> Result<String, (axum::http::StatusCode, String)> {
    if let Some(win) = app_handle.get_window("gemini_main") {
        let _ = win.show();
        let _ = win.unminimize();
        let _ = win.set_focus();

        let js_prompt = serde_json::to_string(&payload.prompt).unwrap_or_default();
        let eval_script = format!(
            r#"
            (function() {{
                if (window.injectAndSendPrompt) {{
                    window.injectAndSendPrompt({});
                }} else {{
                    window.__pendingPrompt = {};
                }}
            }})();
            "#,
            js_prompt, js_prompt
        );

        let _ = win.eval(&eval_script);
        Ok("Prompt dispatched to Gemini window".to_string())
    } else {
        Err((axum::http::StatusCode::NOT_FOUND, "Gemini main window not found".to_string()))
    }
}

async fn handle_perplexity_prompt(
    AxumState(app_handle): AxumState<tauri::AppHandle>,
    Json(payload): Json<PromptDispatchPayload>,
) -> Result<String, (axum::http::StatusCode, String)> {
    if let Some(win) = app_handle.get_window("perplexity_main") {
        let _ = win.show();
        let _ = win.unminimize();
        let _ = win.set_focus();

        let js_prompt = serde_json::to_string(&payload.prompt).unwrap_or_default();
        let eval_script = format!(
            r#"
            (function() {{
                if (window.injectAndSendPrompt) {{
                    window.injectAndSendPrompt({});
                }} else {{
                    const ta = document.querySelector('textarea');
                    if (ta) {{
                        ta.focus();
                        ta.value = {};
                        ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }}
                }}
            }})();
            "#,
            js_prompt, js_prompt
        );

        let _ = win.eval(&eval_script);
        Ok("Prompt dispatched to Perplexity window".to_string())
    } else {
        Err((axum::http::StatusCode::NOT_FOUND, "Perplexity main window not found".to_string()))
    }
}

async fn handle_perplexity_callback(
    Json(payload): Json<PerplexityCallbackPayload>,
) -> Result<String, (axum::http::StatusCode, String)> {
    if resolve_query_callback(&payload.query_id, payload.response, payload.error).await {
        Ok("Callback received".to_string())
    } else {
        Err((axum::http::StatusCode::NOT_FOUND, "Query ID not found or timed out".to_string()))
    }
}

#[derive(serde::Serialize)]
pub struct QueryResponse {
    pub response: String,
    pub query_id: String,
}

async fn handle_perplexity_query(
    AxumState(app_handle): AxumState<tauri::AppHandle>,
    Json(payload): Json<PromptDispatchPayload>,
) -> Result<Json<QueryResponse>, (axum::http::StatusCode, String)> {
    let win = app_handle.get_window("perplexity_main")
        .ok_or_else(|| (axum::http::StatusCode::NOT_FOUND, "Perplexity main window not found".to_string()))?;

    let query_id = format!("pplx_q_{}", std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos());
    let (tx, rx) = tokio::sync::oneshot::channel();

    {
        let mut callbacks = get_query_callbacks().lock().await;
        callbacks.insert(query_id.clone(), tx);
    }

    let js_prompt = serde_json::to_string(&payload.prompt).unwrap_or_default();
    let js_model = serde_json::to_string(&payload.model.unwrap_or_else(|| "claude50sonnetthinking".to_string())).unwrap_or_default();
    let js_session = match payload.session_id {
        Some(s) => serde_json::to_string(&s).unwrap_or_else(|_| "null".to_string()),
        None => "null".to_string(),
    };
    let js_query_id = serde_json::to_string(&query_id).unwrap_or_default();

    let eval_script = format!(
        r#"
        (function() {{
            const qId = {};
            const prompt = {};
            const model = {};
            const session = {};

            function sendDone(resp, err) {{
                const msgObj = {{
                    type: 'query_callback',
                    query_id: qId,
                    queryId: qId,
                    response: resp,
                    error: err,
                    payload: {{ query_id: qId, queryId: qId, response: resp, error: err }}
                }};

                try {{
                    const ws = new WebSocket('ws://127.0.0.1:3031/ws');
                    ws.onopen = function() {{
                        ws.send(JSON.stringify(msgObj));
                        setTimeout(function() {{ ws.close(); }}, 500);
                    }};
                }} catch(e) {{}}

                try {{
                    if (window.__TAURI__ && window.__TAURI__.event) {{
                        window.__TAURI__.event.emit('query_callback_event', msgObj);
                    }}
                }} catch (e) {{}}

                try {{
                    if (window.__TAURI__ && window.__TAURI__.invoke) {{
                        window.__TAURI__.invoke('query_callback', msgObj).catch(function() {{}});
                    }}
                }} catch (e) {{}}

                try {{
                    if (window.__TAURI_INVOKE__) {{
                        window.__TAURI_INVOKE__('query_callback', msgObj);
                    }}
                }} catch (e) {{}}

                try {{
                    if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.ipc) {{
                        window.webkit.messageHandlers.ipc.postMessage(JSON.stringify({{
                            cmd: 'query_callback',
                            callback: 0,
                            error: 0,
                            query_id: qId,
                            queryId: qId,
                            response: resp,
                            error: err,
                            payload: {{ query_id: qId, queryId: qId, response: resp, error: err }}
                        }}));
                    }}
                }} catch (e) {{}}

                try {{
                    fetch('http://127.0.0.1:3031/api/perplexity/callback', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ query_id: qId, response: resp, error: err }})
                    }}).catch(function() {{}});
                }} catch (e) {{}}
            }}

            async function run() {{
                try {{
                    if (!window.__proximaPerplexity || !window.__proximaPerplexity.send) {{
                        throw new Error('Perplexity engine not initialized in webview. URL: ' + window.location.href);
                    }}
                    const answer = await window.__proximaPerplexity.send(prompt, model, null, session);
                    sendDone(answer, null);
                }} catch (err) {{
                    sendDone(null, err.message || String(err));
                }}
            }}

            run();
        }})();
        "#,
        js_query_id, js_prompt, js_model, js_session
    );

    let _ = win.eval(&eval_script);

    match tokio::time::timeout(tokio::time::Duration::from_secs(180), rx).await {
        Ok(Ok(Ok(response_text))) => {
            Ok(Json(QueryResponse {
                response: response_text,
                query_id,
            }))
        }
        Ok(Ok(Err(err_msg))) => {
            Err((axum::http::StatusCode::INTERNAL_SERVER_ERROR, format!("Perplexity execution error: {}", err_msg)))
        }
        Ok(Err(_)) => {
            Err((axum::http::StatusCode::INTERNAL_SERVER_ERROR, "Channel closed before response".to_string()))
        }
        Err(_) => {
            let mut callbacks = get_query_callbacks().lock().await;
            callbacks.remove(&query_id);
            Err((axum::http::StatusCode::GATEWAY_TIMEOUT, "Query timed out after 180 seconds".to_string()))
        }
    }
}

async fn handle_gemini_query(
    AxumState(app_handle): AxumState<tauri::AppHandle>,
    Json(payload): Json<PromptDispatchPayload>,
) -> Result<Json<QueryResponse>, (axum::http::StatusCode, String)> {
    let win = app_handle.get_window("gemini_main")
        .ok_or_else(|| (axum::http::StatusCode::NOT_FOUND, "Gemini main window not found".to_string()))?;

    let query_id = format!("gemini_q_{}", std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos());
    let (tx, rx) = tokio::sync::oneshot::channel();

    {
        let mut callbacks = get_query_callbacks().lock().await;
        callbacks.insert(query_id.clone(), tx);
    }

    let js_prompt = serde_json::to_string(&payload.prompt).unwrap_or_default();
    let js_model = serde_json::to_string(&payload.model.unwrap_or_else(|| "auto".to_string())).unwrap_or_default();
    let js_session = match payload.session_id {
        Some(s) => serde_json::to_string(&s).unwrap_or_else(|_| "null".to_string()),
        None => "null".to_string(),
    };
    let js_query_id = serde_json::to_string(&query_id).unwrap_or_default();

    let eval_script = format!(
        r#"
        (function() {{
            const qId = {};
            const prompt = {};
            const model = {};
            const session = {};

            function sendDone(resp, err) {{
                const msgObj = {{
                    type: 'query_callback',
                    query_id: qId,
                    queryId: qId,
                    response: resp,
                    error: err,
                    payload: {{ query_id: qId, queryId: qId, response: resp, error: err }}
                }};

                try {{
                    const ws = new WebSocket('ws://127.0.0.1:3031/ws');
                    ws.onopen = function() {{
                        ws.send(JSON.stringify(msgObj));
                        setTimeout(function() {{ ws.close(); }}, 500);
                    }};
                }} catch(e) {{}}

                try {{
                    if (window.__TAURI__ && window.__TAURI__.event) {{
                        window.__TAURI__.event.emit('query_callback_event', msgObj);
                    }}
                }} catch (e) {{}}

                try {{
                    if (window.__TAURI__ && window.__TAURI__.invoke) {{
                        window.__TAURI__.invoke('query_callback', msgObj).catch(function() {{}});
                    }}
                }} catch (e) {{}}

                try {{
                    if (window.__TAURI_INVOKE__) {{
                        window.__TAURI_INVOKE__('query_callback', msgObj);
                    }}
                }} catch (e) {{}}

                try {{
                    if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.ipc) {{
                        window.webkit.messageHandlers.ipc.postMessage(JSON.stringify({{
                            cmd: 'query_callback',
                            callback: 0,
                            error: 0,
                            query_id: qId,
                            queryId: qId,
                            response: resp,
                            error: err,
                            payload: {{ query_id: qId, queryId: qId, response: resp, error: err }}
                        }}));
                    }}
                }} catch (e) {{}}

                try {{
                    fetch('http://127.0.0.1:3031/api/gemini/callback', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ query_id: qId, response: resp, error: err }})
                    }}).catch(function() {{}});
                }} catch (e) {{}}
            }}

            async function run() {{
                try {{
                    const engine = window.__proximaGeminiUnified || window.__proximaGemini;
                    if (!engine || !engine.send) {{
                        throw new Error('Gemini engine not initialized in webview. URL: ' + window.location.href);
                    }}
                    const answer = await engine.send(prompt, model, null, session);
                    sendDone(answer, null);
                }} catch (err) {{
                    sendDone(null, err.message || String(err));
                }}
            }}

            run();
        }})();
        "#,
        js_query_id, js_prompt, js_model, js_session
    );

    let _ = win.eval(&eval_script);

    match tokio::time::timeout(tokio::time::Duration::from_secs(180), rx).await {
        Ok(Ok(Ok(response_text))) => {
            Ok(Json(QueryResponse {
                response: response_text,
                query_id,
            }))
        }
        Ok(Ok(Err(err_msg))) => {
            Err((axum::http::StatusCode::INTERNAL_SERVER_ERROR, format!("Gemini execution error: {}", err_msg)))
        }
        Ok(Err(_)) => {
            Err((axum::http::StatusCode::INTERNAL_SERVER_ERROR, "Channel closed before response".to_string()))
        }
        Err(_) => {
            let mut callbacks = get_query_callbacks().lock().await;
            callbacks.remove(&query_id);
            Err((axum::http::StatusCode::GATEWAY_TIMEOUT, "Query timed out after 180 seconds".to_string()))
        }
    }
}

async fn handle_debug_ping(
    AxumState(app_handle): AxumState<tauri::AppHandle>,
) -> Result<String, (axum::http::StatusCode, String)> {
    let win = app_handle.get_window("perplexity_main")
        .ok_or_else(|| (axum::http::StatusCode::NOT_FOUND, "Perplexity main window not found".to_string()))?;

    let (tx, rx) = tokio::sync::oneshot::channel();
    {
        let mut callbacks = get_query_callbacks().lock().await;
        callbacks.insert("test_ping".to_string(), tx);
    }

    let script = r#"
        (function() {
            var diag = 'URL=' + window.location.href + ' | PPLX=' + (typeof window.__proximaPerplexity !== 'undefined') + ' | TAURI=' + (typeof window.__TAURI__ !== 'undefined') + ' | WEBKIT=' + (typeof window.webkit !== 'undefined');
            var msg = {
                type: 'query_callback',
                query_id: 'test_ping',
                queryId: 'test_ping',
                response: diag,
                error: null,
                payload: {
                    query_id: 'test_ping',
                    queryId: 'test_ping',
                    response: diag,
                    error: null
                }
            };
            try {
                var ws = new WebSocket('ws://127.0.0.1:3031/ws');
                ws.onopen = function() {
                    ws.send(JSON.stringify(msg));
                    setTimeout(function() { ws.close(); }, 500);
                };
            } catch(e) {}
            if (window.__TAURI__ && window.__TAURI__.event) {
                window.__TAURI__.event.emit('query_callback_event', msg);
            }
            if (window.__TAURI__ && window.__TAURI__.invoke) {
                window.__TAURI__.invoke('query_callback', msg).catch(function(e) {});
            }
            if (window.__TAURI_INVOKE__) {
                window.__TAURI_INVOKE__('query_callback', msg);
            }
            if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.ipc) {
                window.webkit.messageHandlers.ipc.postMessage(JSON.stringify({
                    cmd: 'query_callback',
                    callback: 0,
                    error: 0,
                    query_id: 'test_ping',
                    queryId: 'test_ping',
                    response: diag,
                    payload: msg.payload
                }));
            }
        })();
    "#;
    let eval_res = win.eval(script);

    match tokio::time::timeout(tokio::time::Duration::from_secs(5), rx).await {
        Ok(Ok(Ok(resp))) => Ok(resp),
        Ok(Ok(Err(err))) => Err((axum::http::StatusCode::INTERNAL_SERVER_ERROR, err)),
        Ok(Err(_)) => Err((axum::http::StatusCode::INTERNAL_SERVER_ERROR, "Channel closed".to_string())),
        Err(_) => {
            let mut callbacks = get_query_callbacks().lock().await;
            callbacks.remove("test_ping");
            Err((axum::http::StatusCode::GATEWAY_TIMEOUT, format!("Ping timed out. eval_res={:?}", eval_res)))
        }
    }
}

async fn handle_debug_ping_gemini(
    AxumState(app_handle): AxumState<tauri::AppHandle>,
) -> Result<String, (axum::http::StatusCode, String)> {
    let win = app_handle.get_window("gemini_main")
        .ok_or_else(|| (axum::http::StatusCode::NOT_FOUND, "Gemini main window not found".to_string()))?;

    let (tx, rx) = tokio::sync::oneshot::channel();
    {
        let mut callbacks = get_query_callbacks().lock().await;
        callbacks.insert("test_ping_gemini".to_string(), tx);
    }

    let script = r#"
        (function() {
            var diag = 'URL=' + window.location.href + ' | GEMINI_UNIFIED=' + (typeof window.__proximaGeminiUnified !== 'undefined') + ' | GEMINI=' + (typeof window.__proximaGemini !== 'undefined') + ' | TAURI=' + (typeof window.__TAURI__ !== 'undefined');
            var msg = {
                type: 'query_callback',
                query_id: 'test_ping_gemini',
                queryId: 'test_ping_gemini',
                response: diag,
                error: null,
                payload: {
                    query_id: 'test_ping_gemini',
                    queryId: 'test_ping_gemini',
                    response: diag,
                    error: null
                }
            };
            try {
                var ws = new WebSocket('ws://127.0.0.1:3031/ws');
                ws.onopen = function() {
                    ws.send(JSON.stringify(msg));
                    setTimeout(function() { ws.close(); }, 500);
                };
            } catch(e) {}
            if (window.__TAURI__ && window.__TAURI__.event) {
                window.__TAURI__.event.emit('query_callback_event', msg);
            }
            if (window.__TAURI__ && window.__TAURI__.invoke) {
                window.__TAURI__.invoke('query_callback', msg).catch(function(e) {});
            }
            if (window.__TAURI_INVOKE__) {
                window.__TAURI_INVOKE__('query_callback', msg);
            }
            if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.ipc) {
                window.webkit.messageHandlers.ipc.postMessage(JSON.stringify({
                    cmd: 'query_callback',
                    callback: 0,
                    error: 0,
                    query_id: 'test_ping_gemini',
                    queryId: 'test_ping_gemini',
                    response: diag,
                    payload: msg.payload
                }));
            }
        })();
    "#;
    let eval_res = win.eval(script);

    match tokio::time::timeout(tokio::time::Duration::from_secs(5), rx).await {
        Ok(Ok(Ok(resp))) => Ok(resp),
        Ok(Ok(Err(err))) => Err((axum::http::StatusCode::INTERNAL_SERVER_ERROR, err)),
        Ok(Err(_)) => Err((axum::http::StatusCode::INTERNAL_SERVER_ERROR, "Channel closed".to_string())),
        Err(_) => {
            let mut callbacks = get_query_callbacks().lock().await;
            callbacks.remove("test_ping_gemini");
            Err((axum::http::StatusCode::GATEWAY_TIMEOUT, format!("Ping timed out. eval_res={:?}", eval_res)))
        }
    }
}

// ---------------------------------------------------------------------------
// Server spawn
// ---------------------------------------------------------------------------

pub fn spawn_axum_server(app_handle: tauri::AppHandle) {
    tauri::async_runtime::spawn(async move {
        let cors = CorsLayer::new()
            .allow_origin(Any)
            .allow_methods(Any)
            .allow_headers(Any);

        let app = Router::new()
            .route("/ws", axum::routing::get(ws_handler))
            .route("/api/context/sync", post(handle_sync))
            .route("/api/revision/commit", post(handle_commit))
            .route("/api/gemini/sync", post(handle_gemini_sync))
            .route("/api/prompt", post(handle_prompt_dispatch))
            .route("/api/gemini/prompt", post(handle_prompt_dispatch))
            .route("/api/gemini/query", post(handle_gemini_query))
            .route("/api/gemini/callback", post(handle_perplexity_callback))
            .route("/api/perplexity/prompt", post(handle_perplexity_prompt))
            .route("/api/perplexity/query", post(handle_perplexity_query))
            .route("/api/perplexity/callback", post(handle_perplexity_callback))
            .route("/api/debug/ping", axum::routing::get(handle_debug_ping))
            .route("/api/debug/ping_gemini", axum::routing::get(handle_debug_ping_gemini))
            .layer(cors)
            .with_state(app_handle);

        let listener = tokio::net::TcpListener::bind("127.0.0.1:3031")
            .await
            .unwrap();
        axum::serve(listener, app).await.unwrap();
    });
}
