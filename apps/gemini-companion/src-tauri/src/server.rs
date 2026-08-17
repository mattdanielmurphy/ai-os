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

#[derive(serde::Deserialize, serde::Serialize, Clone, Debug)]
pub struct AttachmentPayload {
    pub file_path: Option<String>,
    pub file_base64: Option<String>,
    pub filename: Option<String>,
    pub mime_type: Option<String>,
    pub image_token: Option<String>,
}

#[derive(serde::Deserialize, serde::Serialize, Clone, Debug)]
pub struct PromptDispatchPayload {
    pub prompt: String,
    pub model: Option<String>,
    pub session_id: Option<String>,
    pub attachment: Option<AttachmentPayload>,
    pub file_path: Option<String>,
}

fn guess_mime(filename: &str) -> String {
    let lower = filename.to_lowercase();
    if lower.ends_with(".png") { "image/png".to_string() }
    else if lower.ends_with(".jpg") || lower.ends_with(".jpeg") { "image/jpeg".to_string() }
    else if lower.ends_with(".webp") { "image/webp".to_string() }
    else if lower.ends_with(".gif") { "image/gif".to_string() }
    else if lower.ends_with(".pdf") { "application/pdf".to_string() }
    else if lower.ends_with(".txt") { "text/plain".to_string() }
    else if lower.ends_with(".md") { "text/markdown".to_string() }
    else if lower.ends_with(".json") { "application/json".to_string() }
    else if lower.ends_with(".js") || lower.ends_with(".ts") { "application/javascript".to_string() }
    else if lower.ends_with(".mp3") { "audio/mp3".to_string() }
    else if lower.ends_with(".wav") { "audio/wav".to_string() }
    else if lower.ends_with(".mp4") { "video/mp4".to_string() }
    else { "application/octet-stream".to_string() }
}

fn prepare_attachment(
    attachment: Option<AttachmentPayload>,
    file_path: Option<String>,
) -> Option<(String, String, String)> {
    if let Some(att) = attachment {
        if let Some(b64) = att.file_base64 {
            let fname = att.filename.unwrap_or_else(|| "attachment.bin".to_string());
            let mime = att.mime_type.unwrap_or_else(|| guess_mime(&fname));
            return Some((b64, fname, mime));
        }
        if let Some(path_str) = att.file_path {
            if let Ok(bytes) = std::fs::read(&path_str) {
                let b64 = base64::Engine::encode(&base64::engine::general_purpose::STANDARD, &bytes);
                let p = std::path::Path::new(&path_str);
                let fname = att.filename.or_else(|| p.file_name().map(|n| n.to_string_lossy().to_string())).unwrap_or_else(|| "file".to_string());
                let mime = att.mime_type.unwrap_or_else(|| guess_mime(&fname));
                return Some((b64, fname, mime));
            }
        }
    }
    if let Some(path_str) = file_path {
        if let Ok(bytes) = std::fs::read(&path_str) {
            let b64 = base64::Engine::encode(&base64::engine::general_purpose::STANDARD, &bytes);
            let p = std::path::Path::new(&path_str);
            let fname = p.file_name().map(|n| n.to_string_lossy().to_string()).unwrap_or_else(|| "file".to_string());
            let mime = guess_mime(&fname);
            return Some((b64, fname, mime));
        }
    }
    None
}

#[derive(serde::Deserialize)]
pub struct PerplexityCallbackPayload {
    #[serde(alias = "queryId")]
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

async fn wait_for_query_result(
    win: &tauri::Window,
    query_id: &str,
    window_default_title: &str,
    mut rx: tokio::sync::oneshot::Receiver<Result<String, String>>,
    timeout_secs: u64,
) -> Result<String, (axum::http::StatusCode, String)> {
    let start_time = std::time::Instant::now();
    let timeout_duration = std::time::Duration::from_secs(timeout_secs);
    let res_prefix = format!("AIOS_RES_{}:", query_id);
    let err_prefix = format!("AIOS_ERR_{}:", query_id);

    loop {
        if start_time.elapsed() > timeout_duration {
            let mut callbacks = get_query_callbacks().lock().await;
            callbacks.remove(query_id);
            let _ = win.set_title(window_default_title);
            return Err((
                axum::http::StatusCode::GATEWAY_TIMEOUT,
                format!("Query {} timed out after {} seconds", query_id, timeout_secs),
            ));
        }

        // 1. Check oneshot channel (non-blocking)
        match rx.try_recv() {
            Ok(Ok(response)) => {
                let _ = win.set_title(window_default_title);
                return Ok(response);
            }
            Ok(Err(err_msg)) => {
                let _ = win.set_title(window_default_title);
                return Err((
                    axum::http::StatusCode::INTERNAL_SERVER_ERROR,
                    format!("Execution error: {}", err_msg),
                ));
            }
            Err(tokio::sync::oneshot::error::TryRecvError::Closed) => {
                // Sender closed, check title bridge below
            }
            Err(tokio::sync::oneshot::error::TryRecvError::Empty) => {
                // Channel empty, check title bridge below
            }
        }

        // 2. Check window title zero-network bridge
        if let Ok(title) = win.title() {
            if let Some(pos) = title.find(&res_prefix) {
                let b64_str = &title[pos + res_prefix.len()..];
                let decoded_bytes = base64::Engine::decode(&base64::engine::general_purpose::STANDARD, b64_str)
                    .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, format!("Base64 decode error: {}", e)))?;
                let json_str = String::from_utf8(decoded_bytes)
                    .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, format!("UTF-8 parse error: {}", e)))?;
                let payload: PerplexityCallbackPayload = serde_json::from_str(&json_str)
                    .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, format!("JSON parse error: {}", e)))?;

                let mut callbacks = get_query_callbacks().lock().await;
                callbacks.remove(query_id);

                let _ = win.set_title(window_default_title);

                if let Some(err) = payload.error {
                    return Err((
                        axum::http::StatusCode::INTERNAL_SERVER_ERROR,
                        format!("Execution error: {}", err),
                    ));
                }
                return Ok(payload.response.unwrap_or_default());
            } else if let Some(pos) = title.find(&err_prefix) {
                let err_str = title[pos + err_prefix.len()..].to_string();
                let mut callbacks = get_query_callbacks().lock().await;
                callbacks.remove(query_id);
                let _ = win.set_title(window_default_title);
                return Err((
                    axum::http::StatusCode::INTERNAL_SERVER_ERROR,
                    format!("Execution error: {}", err_str),
                ));
            }
        }

        tokio::time::sleep(tokio::time::Duration::from_millis(50)).await;
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

    let att_data = prepare_attachment(payload.attachment, payload.file_path);
    let (js_file_b64, js_filename, js_mime) = match att_data {
        Some((b64, fname, mime)) => (
            serde_json::to_string(&b64).unwrap_or_default(),
            serde_json::to_string(&fname).unwrap_or_default(),
            serde_json::to_string(&mime).unwrap_or_default(),
        ),
        None => ("null".to_string(), "null".to_string(), "null".to_string()),
    };

    let js_prompt = serde_json::to_string(&payload.prompt).unwrap_or_default();
    let js_model = serde_json::to_string(&payload.model.unwrap_or_else(|| "grok46medium".to_string())).unwrap_or_default();
    let js_session = match payload.session_id {
        Some(s) => serde_json::to_string(&s).unwrap_or_else(|_| "null".to_string()),
        None => "null".to_string(),
    };
    let js_query_id = serde_json::to_string(&query_id).unwrap_or_default();
    let pplx_engine = std::fs::read_to_string("/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/engines/perplexity-engine.js").unwrap_or_default();

    let eval_script = format!(
        r#"
        {}
        (function() {{
            const qId = {};
            const prompt = {};
            const model = {};
            const session = {};
            const fileB64 = {};
            const fileName = {};
            const fileMime = {};

            function sendDone(resp, err) {{
                var payload = {{ query_id: qId, queryId: qId, response: resp || null, error: err || null }};
                try {{
                    if (window.__TAURI__ && window.__TAURI__.invoke) {{
                        window.__TAURI__.invoke('query_callback', payload).catch(function(e) {{}});
                    }} else if (window.__TAURI_INVOKE__) {{
                        window.__TAURI_INVOKE__('query_callback', payload);
                    }}
                }} catch(e) {{}}
                try {{
                    if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.ipc) {{
                        window.webkit.messageHandlers.ipc.postMessage(JSON.stringify({{
                            cmd: 'query_callback',
                            callback: 0,
                            error: 0,
                            query_id: qId,
                            queryId: qId,
                            response: resp || null,
                            err_msg: err || null,
                            payload: payload
                        }}));
                    }}
                }} catch(e) {{}}
                try {{
                    fetch('http://127.0.0.1:3031/api/perplexity/callback', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(payload)
                    }}).catch(function() {{}});
                }} catch(e) {{}}
                try {{
                    var jsonStr = JSON.stringify(payload);
                    var b64 = btoa(unescape(encodeURIComponent(jsonStr)));
                    document.title = 'AIOS_RES_' + qId + ':' + b64;
                }} catch(e) {{
                    document.title = 'AIOS_ERR_' + qId + ':' + (err || e.message);
                }}
            }}

            async function run() {{
                try {{
                    const pplx = window.__aiosPerplexity || window.__proximaPerplexity;
                    if (!pplx || !pplx.send) {{
                        throw new Error('Perplexity engine not initialized in webview. URL: ' + window.location.href);
                    }}
                    let attachmentsObj = null;
                    if (fileB64 && fileName && fileMime) {{
                        if (pplx.uploadFileToPerplexity) {{
                            const s3Url = await pplx.uploadFileToPerplexity(fileB64, fileName, fileMime);
                            attachmentsObj = {{
                                imageToken: s3Url,
                                filename: fileName,
                                mimeType: fileMime
                            }};
                        }}
                    }}
                    const answer = await pplx.send(prompt, model, attachmentsObj, session);
                    sendDone(answer, null);
                }} catch (err) {{
                    sendDone(null, err.message || String(err));
                }}
            }}

            run();
        }})();
        "#,
        pplx_engine, js_query_id, js_prompt, js_model, js_session, js_file_b64, js_filename, js_mime
    );

    let _ = win.eval(&eval_script);

    let response = wait_for_query_result(&win, &query_id, "Perplexity", rx, 600).await?;
    Ok(Json(QueryResponse {
        response,
        query_id,
    }))
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

    let att_data = prepare_attachment(payload.attachment, payload.file_path);
    let (js_file_b64, js_filename, js_mime) = match att_data {
        Some((b64, fname, mime)) => (
            serde_json::to_string(&b64).unwrap_or_default(),
            serde_json::to_string(&fname).unwrap_or_default(),
            serde_json::to_string(&mime).unwrap_or_default(),
        ),
        None => ("null".to_string(), "null".to_string(), "null".to_string()),
    };

    let js_prompt = serde_json::to_string(&payload.prompt).unwrap_or_default();
    let js_model = serde_json::to_string(&payload.model.unwrap_or_else(|| "auto".to_string())).unwrap_or_default();
    let js_session = match payload.session_id {
        Some(s) => serde_json::to_string(&s).unwrap_or_else(|_| "null".to_string()),
        None => "null".to_string(),
    };
    let js_query_id = serde_json::to_string(&query_id).unwrap_or_default();
    let gemini_engine = std::fs::read_to_string("/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/engines/gemini-engine.js").unwrap_or_default();

    let eval_script = format!(
        r#"
        {}
        (function() {{
            const qId = {};
            const prompt = {};
            const model = {};
            const session = {};
            const fileB64 = {};
            const fileName = {};
            const fileMime = {};

            function sendDone(resp, err) {{
                var payload = {{ query_id: qId, queryId: qId, response: resp || null, error: err || null }};
                try {{
                    if (window.__TAURI__ && window.__TAURI__.invoke) {{
                        window.__TAURI__.invoke('query_callback', payload).catch(function(e) {{}});
                    }} else if (window.__TAURI_INVOKE__) {{
                        window.__TAURI_INVOKE__('query_callback', payload);
                    }}
                }} catch(e) {{}}
                try {{
                    if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.ipc) {{
                        window.webkit.messageHandlers.ipc.postMessage(JSON.stringify({{
                            cmd: 'query_callback',
                            callback: 0,
                            error: 0,
                            query_id: qId,
                            queryId: qId,
                            response: resp || null,
                            err_msg: err || null,
                            payload: payload
                        }}));
                    }}
                }} catch(e) {{}}
                try {{
                    fetch('http://127.0.0.1:3031/api/gemini/callback', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(payload)
                    }}).catch(function() {{}});
                }} catch(e) {{}}
                try {{
                    var jsonStr = JSON.stringify(payload);
                    var b64 = btoa(unescape(encodeURIComponent(jsonStr)));
                    document.title = 'AIOS_RES_' + qId + ':' + b64;
                }} catch(e) {{
                    document.title = 'AIOS_ERR_' + qId + ':' + (err || e.message);
                }}
            }}

            async function run() {{
                try {{
                    const engine = window.__aiosGeminiUnified || window.__aiosGemini || window.__proximaGeminiUnified || window.__proximaGemini;
                    if (!engine || !engine.send) {{
                        throw new Error('Gemini engine not initialized in webview. URL: ' + window.location.href);
                    }}
                    let attachmentsObj = null;
                    if (fileB64 && fileName && fileMime) {{
                        if (engine.uploadFileToGoogle) {{
                            const token = await engine.uploadFileToGoogle(fileB64, fileName, fileMime);
                            attachmentsObj = {{
                                imageToken: token,
                                filename: fileName,
                                mimeType: fileMime
                            }};
                        }}
                    }}
                    const answer = await engine.send(prompt, model, attachmentsObj, session);
                    sendDone(answer, null);
                }} catch (err) {{
                    sendDone(null, err.message || String(err));
                }}
            }}

            run();
        }})();
        "#,
        gemini_engine, js_query_id, js_prompt, js_model, js_session, js_file_b64, js_filename, js_mime
    );

    let _ = win.eval(&eval_script);

    let response = wait_for_query_result(&win, &query_id, "Gemini", rx, 600).await?;
    Ok(Json(QueryResponse {
        response,
        query_id,
    }))
}

// ---------------------------------------------------------------------------
// OpenAI-Compatible REST Gateway (/v1/chat/completions & /v1/models)
// ---------------------------------------------------------------------------

#[derive(serde::Deserialize, Debug)]
pub struct ChatMessage {
    pub role: String,
    pub content: serde_json::Value,
}

#[derive(serde::Deserialize, Debug)]
pub struct OpenAIChatRequest {
    pub model: Option<String>,
    pub messages: Vec<ChatMessage>,
    pub stream: Option<bool>,
    pub session_id: Option<String>,
}

#[derive(serde::Serialize, Debug)]
pub struct OpenAIChoiceMessage {
    pub role: String,
    pub content: String,
}

#[derive(serde::Serialize, Debug)]
pub struct OpenAIChoice {
    pub index: usize,
    pub message: OpenAIChoiceMessage,
    pub finish_reason: String,
}

#[derive(serde::Serialize, Debug)]
pub struct OpenAIUsage {
    pub prompt_tokens: usize,
    pub completion_tokens: usize,
    pub total_tokens: usize,
}

#[derive(serde::Serialize, Debug)]
pub struct OpenAIChatResponse {
    pub id: String,
    pub object: String,
    pub created: u64,
    pub model: String,
    pub choices: Vec<OpenAIChoice>,
    pub usage: OpenAIUsage,
}

#[derive(serde::Serialize, Debug)]
pub struct OpenAIModelItem {
    pub id: String,
    pub object: String,
    pub owned_by: String,
}

#[derive(serde::Serialize, Debug)]
pub struct OpenAIModelList {
    pub object: String,
    pub data: Vec<OpenAIModelItem>,
}

async fn handle_openai_models() -> Json<OpenAIModelList> {
    Json(OpenAIModelList {
        object: "list".to_string(),
        data: vec![
            OpenAIModelItem { id: "gemini".to_string(), object: "model".to_string(), owned_by: "google".to_string() },
            OpenAIModelItem { id: "gemini-3.5-flash".to_string(), object: "model".to_string(), owned_by: "google".to_string() },
            OpenAIModelItem { id: "gemini-3.1-pro".to_string(), object: "model".to_string(), owned_by: "google".to_string() },
            OpenAIModelItem { id: "gemini-3.1-flash-lite".to_string(), object: "model".to_string(), owned_by: "google".to_string() },
            OpenAIModelItem { id: "perplexity".to_string(), object: "model".to_string(), owned_by: "perplexity".to_string() },
            OpenAIModelItem { id: "sonar".to_string(), object: "model".to_string(), owned_by: "perplexity".to_string() },
            OpenAIModelItem { id: "sonnet".to_string(), object: "model".to_string(), owned_by: "perplexity".to_string() },
            OpenAIModelItem { id: "claude50sonnetthinking".to_string(), object: "model".to_string(), owned_by: "perplexity".to_string() },
        ],
    })
}

async fn handle_openai_chat(
    AxumState(app_handle): AxumState<tauri::AppHandle>,
    Json(req): Json<OpenAIChatRequest>,
) -> Result<axum::response::Response, (axum::http::StatusCode, String)> {
    let mut combined_prompt = String::new();
    let mut attachment: Option<AttachmentPayload> = None;

    for msg in &req.messages {
        let role = &msg.role;
        match &msg.content {
            serde_json::Value::String(s) => {
                if !combined_prompt.is_empty() {
                    combined_prompt.push_str("\n\n");
                }
                if role == "system" {
                    combined_prompt.push_str(&format!("[System Instructions]:\n{}", s));
                } else if role == "user" {
                    combined_prompt.push_str(s);
                } else {
                    combined_prompt.push_str(&format!("[{role}]:\n{}", s));
                }
            }
            serde_json::Value::Array(parts) => {
                for p in parts {
                    if let Some(t) = p.get("text").and_then(|v| v.as_str()) {
                        if !combined_prompt.is_empty() {
                            combined_prompt.push_str("\n\n");
                        }
                        combined_prompt.push_str(t);
                    }
                    if let Some(image_url_obj) = p.get("image_url") {
                        if let Some(url) = image_url_obj.get("url").and_then(|v| v.as_str()) {
                            if url.starts_with("data:") {
                                if let Some((header, b64)) = url.split_once(',') {
                                    let mime = header.trim_start_matches("data:").trim_end_matches(";base64");
                                    attachment = Some(AttachmentPayload {
                                        file_path: None,
                                        file_base64: Some(b64.to_string()),
                                        filename: Some("image.png".to_string()),
                                        mime_type: Some(mime.to_string()),
                                        image_token: None,
                                    });
                                }
                            }
                        }
                    }
                }
            }
            _ => {}
        }
    }

    let model_str = req.model.clone().unwrap_or_else(|| "gemini".to_string()).to_lowercase();
    let is_perplexity = model_str.contains("perplexity") || model_str == "sonar" || model_str == "sonnet" || model_str.contains("claude");

    let dispatch_payload = PromptDispatchPayload {
        prompt: combined_prompt,
        model: req.model.clone(),
        session_id: req.session_id.clone(),
        attachment,
        file_path: None,
    };

    let result_text = if is_perplexity {
        let resp = handle_perplexity_query(AxumState(app_handle), Json(dispatch_payload)).await?;
        resp.0.response
    } else {
        let resp = handle_gemini_query(AxumState(app_handle), Json(dispatch_payload)).await?;
        resp.0.response
    };

    let created = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();
    let resp_id = format!("chatcmpl-{}", std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos());

    let is_stream = req.stream.unwrap_or(false);
    if is_stream {
        let chunk1 = serde_json::json!({
            "id": resp_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": req.model.clone().unwrap_or_else(|| "gemini".to_string()),
            "choices": [{
                "index": 0,
                "delta": {
                    "role": "assistant",
                    "content": result_text
                },
                "finish_reason": null
            }]
        });
        let chunk2 = serde_json::json!({
            "id": resp_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": req.model.unwrap_or_else(|| "gemini".to_string()),
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }]
        });

        let sse_body = format!(
            "data: {}\n\ndata: {}\n\ndata: [DONE]\n\n",
            serde_json::to_string(&chunk1).unwrap(),
            serde_json::to_string(&chunk2).unwrap()
        );

        let response = axum::response::Response::builder()
            .header("Content-Type", "text/event-stream")
            .header("Cache-Control", "no-cache")
            .header("Connection", "keep-alive")
            .body(axum::body::Body::from(sse_body))
            .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

        Ok(response)
    } else {
        let prompt_tokens = 50;
        let completion_tokens = result_text.split_whitespace().count() * 4 / 3;
        let response_obj = OpenAIChatResponse {
            id: resp_id,
            object: "chat.completion".to_string(),
            created,
            model: req.model.unwrap_or_else(|| "gemini".to_string()),
            choices: vec![
                OpenAIChoice {
                    index: 0,
                    message: OpenAIChoiceMessage {
                        role: "assistant".to_string(),
                        content: result_text,
                    },
                    finish_reason: "stop".to_string(),
                }
            ],
            usage: OpenAIUsage {
                prompt_tokens,
                completion_tokens,
                total_tokens: prompt_tokens + completion_tokens,
            },
        };

        let response = axum::response::Response::builder()
            .header("Content-Type", "application/json")
            .body(axum::body::Body::from(serde_json::to_string(&response_obj).unwrap()))
            .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

        Ok(response)
    }
}

async fn handle_debug_ping(
    AxumState(app_handle): AxumState<tauri::AppHandle>,
) -> Result<String, (axum::http::StatusCode, String)> {
    let win = app_handle.get_window("perplexity_main")
        .ok_or_else(|| (axum::http::StatusCode::NOT_FOUND, "Perplexity main window not found".to_string()))?;

    let ping_id = format!("ping_{}", std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos());
    let (tx, rx) = tokio::sync::oneshot::channel();
    {
        let mut callbacks = get_query_callbacks().lock().await;
        callbacks.insert(ping_id.clone(), tx);
    }

    let pplx_engine = std::fs::read_to_string("/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/engines/perplexity-engine.js").unwrap_or_default();
    let js_ping_id = serde_json::to_string(&ping_id).unwrap_or_default();
    let script = format!(
        r#"
        {}
        (function() {{
            var qId = {};
            var diag = 'URL=' + window.location.href + ' | PPLX=' + (typeof window.__aiosPerplexity !== 'undefined') + ' | TAURI=' + (typeof window.__TAURI__ !== 'undefined') + ' | WEBKIT=' + (typeof window.webkit !== 'undefined' && typeof window.webkit.messageHandlers !== 'undefined' && typeof window.webkit.messageHandlers.ipc !== 'undefined');
            var payload = {{ query_id: qId, queryId: qId, response: diag, error: null }};
            try {{
                if (window.__TAURI__ && window.__TAURI__.invoke) {{
                    window.__TAURI__.invoke('query_callback', payload).catch(function(e) {{}});
                }} else if (window.__TAURI_INVOKE__) {{
                    window.__TAURI_INVOKE__('query_callback', payload);
                }}
            }} catch(e) {{}}
            try {{
                if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.ipc) {{
                    window.webkit.messageHandlers.ipc.postMessage(JSON.stringify({{
                        cmd: 'query_callback',
                        callback: 0,
                        error: 0,
                        query_id: qId,
                        queryId: qId,
                        response: diag,
                        err_msg: null,
                        payload: payload
                    }}));
                }}
            }} catch(e) {{}}
            try {{
                fetch('http://127.0.0.1:3031/api/perplexity/callback', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payload)
                }}).catch(function() {{}});
            }} catch(e) {{}}
            try {{
                var jsonStr = JSON.stringify(payload);
                var b64 = btoa(unescape(encodeURIComponent(jsonStr)));
                document.title = 'AIOS_RES_' + qId + ':' + b64;
            }} catch(e) {{
                document.title = 'AIOS_ERR_' + qId + ':' + e.message;
            }}
        }})();
        "#,
        pplx_engine, js_ping_id
    );
    let _ = win.eval(&script);

    wait_for_query_result(&win, &ping_id, "Perplexity", rx, 5).await
}

async fn handle_debug_ping_gemini(
    AxumState(app_handle): AxumState<tauri::AppHandle>,
) -> Result<String, (axum::http::StatusCode, String)> {
    let win = app_handle.get_window("gemini_main")
        .ok_or_else(|| (axum::http::StatusCode::NOT_FOUND, "Gemini main window not found".to_string()))?;

    let ping_id = format!("ping_gemini_{}", std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos());
    let (tx, rx) = tokio::sync::oneshot::channel();
    {
        let mut callbacks = get_query_callbacks().lock().await;
        callbacks.insert(ping_id.clone(), tx);
    }

    let gemini_engine = std::fs::read_to_string("/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/engines/gemini-engine.js").unwrap_or_default();
    let js_ping_id = serde_json::to_string(&ping_id).unwrap_or_default();
    let script = format!(
        r#"
        {}
        (function() {{
            var qId = {};
            var diag = 'URL=' + window.location.href + ' | GEMINI=' + (typeof window.__aiosGeminiUnified !== 'undefined' || typeof window.__aiosGemini !== 'undefined') + ' | TAURI=' + (typeof window.__TAURI__ !== 'undefined') + ' | WEBKIT=' + (typeof window.webkit !== 'undefined' && typeof window.webkit.messageHandlers !== 'undefined' && typeof window.webkit.messageHandlers.ipc !== 'undefined');
            var payload = {{ query_id: qId, queryId: qId, response: diag, error: null }};
            try {{
                if (window.__TAURI__ && window.__TAURI__.invoke) {{
                    window.__TAURI__.invoke('query_callback', payload).catch(function(e) {{}});
                }} else if (window.__TAURI_INVOKE__) {{
                    window.__TAURI_INVOKE__('query_callback', payload);
                }}
            }} catch(e) {{}}
            try {{
                if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.ipc) {{
                    window.webkit.messageHandlers.ipc.postMessage(JSON.stringify({{
                        cmd: 'query_callback',
                        callback: 0,
                        error: 0,
                        query_id: qId,
                        queryId: qId,
                        response: diag,
                        err_msg: null,
                        payload: payload
                    }}));
                }}
            }} catch(e) {{}}
            try {{
                fetch('http://127.0.0.1:3031/api/gemini/callback', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payload)
                }}).catch(function() {{}});
            }} catch(e) {{}}
            try {{
                var jsonStr = JSON.stringify(payload);
                var b64 = btoa(unescape(encodeURIComponent(jsonStr)));
                document.title = 'AIOS_RES_' + qId + ':' + b64;
            }} catch(e) {{
                document.title = 'AIOS_ERR_' + qId + ':' + e.message;
            }}
        }})();
        "#,
        gemini_engine, js_ping_id
    );
    let _ = win.eval(&script);

    wait_for_query_result(&win, &ping_id, "Gemini", rx, 5).await
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
            .route("/v1/chat/completions", post(handle_openai_chat))
            .route("/v1/models", axum::routing::get(handle_openai_models))
            .layer(cors)
            .with_state(app_handle);

        let listener = tokio::net::TcpListener::bind("127.0.0.1:3031")
            .await
            .unwrap();
        axum::serve(listener, app).await.unwrap();
    });
}
