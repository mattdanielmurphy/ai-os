use axum::{
    routing::{get, post},
    Router, Json,
};
use tower_http::cors::CorsLayer;
use serde_json::json;
use crate::{cloud_sync, fs_bridge, shell_bridge, context_snapshot};

async fn handle_status() -> Json<serde_json::Value> {
    Json(json!({
        "status": "ok",
        "port": 19223,
        "version": "proxima-lite-0.1.0"
    }))
}

async fn handle_thread_save(
    Json(payload): Json<cloud_sync::CloudThreadIngestPayload>,
) -> Json<serde_json::Value> {
    cloud_sync::handle_cloud_ingest(Json(payload)).await
}

async fn handle_bridge_context() -> Json<serde_json::Value> {
    let project_root = std::env::var("AIOS_INITIAL_PROJECT").unwrap_or_else(|_| ".".to_string());
    match context_snapshot::get_project_snapshot(&project_root).await {
        Ok(snapshot) => Json(json!({ "status": "ok", "context": snapshot })),
        Err(e) => Json(json!({ "status": "error", "message": e })),
    }
}

#[derive(serde::Deserialize)]
struct BridgeExecPayload {
    action: String,
    path: Option<String>,
    content: Option<String>,
    command: Option<String>,
    cwd: Option<String>,
}

async fn handle_bridge_execute(
    Json(payload): Json<BridgeExecPayload>,
) -> Json<serde_json::Value> {
    let project_root = std::env::var("AIOS_INITIAL_PROJECT").unwrap_or_else(|_| ".".to_string());
    match payload.action.as_str() {
        "read_file" => {
            let p = payload.path.unwrap_or_default();
            match fs_bridge::read_file(&p, &project_root) {
                Ok(c) => Json(json!({ "status": "ok", "content": c })),
                Err(e) => Json(json!({ "status": "error", "message": e })),
            }
        }
        "write_file" => {
            let p = payload.path.unwrap_or_default();
            let c = payload.content.unwrap_or_default();
            match fs_bridge::write_file(&p, &c, &project_root) {
                Ok(_) => Json(json!({ "status": "ok" })),
                Err(e) => Json(json!({ "status": "error", "message": e })),
            }
        }
        "list_dir" => {
            let p = payload.path.unwrap_or_default();
            match fs_bridge::list_dir(&p, &project_root) {
                Ok(files) => Json(json!({ "status": "ok", "files": files })),
                Err(e) => Json(json!({ "status": "error", "message": e })),
            }
        }
        "run_command" => {
            let cmd = payload.command.unwrap_or_default();
            let cwd = payload.cwd.unwrap_or(project_root);
            match shell_bridge::execute_command(&cmd, &cwd).await {
                Ok((code, stdout, stderr)) => Json(json!({
                    "status": "ok",
                    "exit_code": code,
                    "stdout": stdout,
                    "stderr": stderr
                })),
                Err(e) => Json(json!({ "status": "error", "message": e })),
            }
        }
        unknown => Json(json!({ "status": "error", "message": format!("Unknown action: {}", unknown) })),
    }
}

pub async fn start_proxy_server(_app_handle: tauri::AppHandle) -> Result<(), String> {
    let app = Router::new()
        .route("/api/status", get(handle_status))
        .route("/api/thread/save", post(handle_thread_save))
        .route("/api/cloud-sync/status", get(cloud_sync::handle_cloud_status))
        .route("/api/cloud-sync/ingest", post(cloud_sync::handle_cloud_ingest))
        .route("/api/bridge/context", get(handle_bridge_context))
        .route("/api/bridge/execute", post(handle_bridge_execute))
        .layer(CorsLayer::permissive());

    let listener = match tokio::net::TcpListener::bind("127.0.0.1:19223").await {
        Ok(l) => l,
        Err(e) => {
            eprintln!("[Proxima-Lite] Failed to bind proxy port 19223 (is another instance running?): {}", e);
            return Err(e.to_string());
        }
    };

    println!("[Proxima-Lite] Proxy daemon running on http://127.0.0.1:19223");
    if let Err(e) = axum::serve(listener, app).await {
        eprintln!("[Proxima-Lite] Proxy daemon server error: {}", e);
        return Err(e.to_string());
    }

    
pub fn spawn_proxy_server(app_handle: tauri::AppHandle) {
    tauri::async_runtime::spawn(async move {
        let _ = start_proxy_server(app_handle).await;
    });
}

