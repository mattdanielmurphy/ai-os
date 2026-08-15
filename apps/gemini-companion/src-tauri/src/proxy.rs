use axum::{routing::{get, post}, Json, Router, extract::State};
use serde::{Deserialize, Serialize};
use std::fs::{self, File};
use std::io::{Write};
use std::path::{PathBuf};
use tower_http::cors::CorsLayer;
use serde_json::Value;

#[derive(Serialize, Deserialize)]
struct SaveThreadRequest {
    provider: String,
    thread_id: String,
    title: String,
    messages: Vec<Value>,
}

async fn status_handler() -> Json<Value> {
    Json(serde_json::json!({"status": "ok", "port": 19223, "version": "proxima-lite-0.1.0"}))
}

async fn save_thread_handler(Json(payload): Json<SaveThreadRequest>) -> Json<Value> {
    let filename = format!("/Users/matt/projects/ai-os/context/threads/{}_{}.md", payload.provider, payload.thread_id);
    let path = PathBuf::from(&filename);
    
    // Simple YAML frontmatter + content
    let content = format!(
        "---\nprovider: {}\nthread_id: {}\ntitle: {}\n---\n{}",
        payload.provider, payload.thread_id, payload.title,
        serde_json::to_string_pretty(&payload.messages).unwrap_or_default()
    );

    // Atomic write via .tmp
    let tmp_path = path.with_extension("tmp");
    if let Ok(mut file) = File::create(&tmp_path) {
        let _ = file.write_all(content.as_bytes());
        let _ = fs::rename(tmp_path, path);
    }

    Json(serde_json::json!({"status": "saved"}))
}

pub async fn start_proxy_server(_app_handle: tauri::AppHandle) {
    let app = Router::new()
        .route("/api/status", get(status_handler))
        .route("/api/thread/save", post(save_thread_handler))
        .layer(CorsLayer::permissive());

    let listener = tokio::net::TcpListener::bind("127.0.0.1:19223").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
