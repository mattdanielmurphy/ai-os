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
    host_tx: Option<mpsc::UnboundedSender<Message>>,
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

    let my_client_id = format!(
        "client_{}",
        CLIENT_ID_COUNTER.fetch_add(1, Ordering::SeqCst)
    );
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
                                state.host_tx = Some(tx.clone());
                            } else if role == "client" {
                                registered_role = Some("client");
                                let mut state = get_ws_state().lock().unwrap();
                                state.clients
                                    .insert(my_client_id.clone(), tx.clone());
                            }
                        }
                        "invoke" => {
                            let mut payload = val.clone();
                            payload["client_id"] = serde_json::Value::String(
                                my_client_id.clone(),
                            );
                            let forward_msg =
                                Message::Text(payload.to_string().into());
                            let state = get_ws_state().lock().unwrap();
                            if let Some(host_tx) = &state.host_tx {
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
            state.host_tx = None;
        } else {
            state.clients.remove(&client_id_clone);
        }
    }
    write_task.abort();
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
            .layer(cors)
            .with_state(app_handle);

        let listener = tokio::net::TcpListener::bind("127.0.0.1:3031")
            .await
            .unwrap();
        axum::serve(listener, app).await.unwrap();
    });
}
