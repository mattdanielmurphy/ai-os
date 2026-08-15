use axum::{Json, Router, routing::{get, post}};
use serde::{Deserialize, Serialize};
use std::fs::{self, File};
use std::io::{Write, Read};
use std::path::Path;
use sha2::{Sha256, Digest};
use tauri::Manager;
use tokio::time::{self, Duration};

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct ThreadMessage {
    pub role: String,
    pub content: String,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct CloudThreadIngestPayload {
    pub provider: String,
    pub thread_id: String,
    pub title: String,
    pub updated_at: Option<i64>,
    pub messages: Vec<ThreadMessage>,
}

pub async fn handle_cloud_ingest(Json(payload): Json<CloudThreadIngestPayload>) -> Json<serde_json::Value> {
    match save_cloud_thread(payload) {
        Ok(_) => Json(serde_json::json!({"status": "success"})),
        Err(e) => Json(serde_json::json!({"status": "error", "message": e.to_string()})),
    }
}

pub async fn handle_cloud_status() -> Json<serde_json::Value> {
    Json(serde_json::json!({"status": "ok", "sync_enabled": true}))
}

#[allow(dead_code)]
pub fn router() -> Router {
    Router::new()
        .route("/api/cloud-sync/status", get(handle_cloud_status))
        .route("/api/cloud-sync/ingest", post(handle_cloud_ingest))
}

fn save_cloud_thread(payload: CloudThreadIngestPayload) -> Result<(), Box<dyn std::error::Error>> {
    let base_dir = Path::new("/Users/matt/projects/ai-os/context/threads");
    let target_dir = base_dir.join(&payload.provider);
    fs::create_dir_all(&target_dir)?;

    let file_path = target_dir.join(format!("{}.md", payload.thread_id));
    
    let mut markdown = format!(
        "---\ntitle: {}\nprovider: {}\nthread_id: {}\nupdated_at: {:?}\n---\n\n",
        payload.title, payload.provider, payload.thread_id, payload.updated_at
    );
    for msg in payload.messages {
        markdown.push_str(&format!("**{}**: {}\n\n", msg.role, msg.content));
    }

    let mut hasher = Sha256::new();
    hasher.update(markdown.as_bytes());
    let new_hash = format!("{:x}", hasher.finalize());

    if file_path.exists() {
        let mut file = File::open(&file_path)?;
        let mut existing_content = String::new();
        file.read_to_string(&mut existing_content)?;
        let mut hasher = Sha256::new();
        hasher.update(existing_content.as_bytes());
        if format!("{:x}", hasher.finalize()) == new_hash {
            return Ok(());
        }
    }

    let temp_path = file_path.with_extension("tmp");
    let mut file = File::create(&temp_path)?;
    file.write_all(markdown.as_bytes())?;
    fs::rename(temp_path, file_path)?;

    Ok(())
}

pub fn start_sync_scheduler(app_handle: tauri::AppHandle) {
    tauri::async_runtime::spawn(async move {
        let mut interval = time::interval(Duration::from_secs(15 * 60));
        loop {
            interval.tick().await;
            app_handle.emit_all("run-history-sync", ()).unwrap_or_default();
        }
    });
}
