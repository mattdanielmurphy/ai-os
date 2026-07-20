use std::sync::{Arc, Mutex};
use std::collections::HashMap;
use portable_pty::MasterPty;
use std::io::Write;

// ---------------------------------------------------------------------------
// Core data types
// ---------------------------------------------------------------------------

/// Project session containing its own PTY channels and shell process details
#[allow(dead_code)]
pub struct ProjectSession {
    pub claude_writer: Option<Box<dyn Write + Send>>,
    pub claude_master: Option<Box<dyn MasterPty + Send>>,
    pub claude_pid: Option<u32>,
    pub agy_writer: Option<Box<dyn Write + Send>>,
    pub agy_master: Option<Box<dyn MasterPty + Send>>,
    pub agy_pid: Option<u32>,
    pub hermes_writer: Option<Box<dyn Write + Send>>,
    pub hermes_master: Option<Box<dyn MasterPty + Send>>,
    pub hermes_pid: Option<u32>,
    pub mini_writer: Box<dyn Write + Send>,
    pub mini_master: Box<dyn MasterPty + Send>,
    pub mini_pid: u32,
    pub project_path: String,
    pub thread_id: String,
    pub last_accessed: std::time::SystemTime,
}

pub struct AppState {
    pub sessions: Arc<Mutex<HashMap<String, ProjectSession>>>,
    pub active_project: Arc<Mutex<Option<String>>>,
    pub app_handle: tauri::AppHandle,
    pub last_active_account: Arc<Mutex<Option<String>>>,
}

#[derive(Clone, serde::Serialize)]
pub struct Payload {
    pub data: String,
    pub project_path: String,
    pub terminal_type: String,
}

#[derive(Clone, serde::Serialize)]
pub struct SwitchResult {
    pub shell_pid: u32,
    pub is_new_session: bool,
    pub hermes_ws_port: u16,
}

#[derive(Clone, serde::Serialize)]
pub struct PauseStatusPayload {
    pub project_path: String,
    pub status: String,
}

#[derive(Clone, serde::Serialize)]
pub struct ThreadLog {
    pub id: String,
    pub latest_leaf_id: String,
    pub title: String,
    pub snippet: String,
    pub filepath: String,
    pub mtime: u64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub detected_project_path: Option<String>,
}

#[derive(Clone, serde::Serialize)]
pub struct ThreadSearchResult {
    pub thread: ThreadLog,
    pub score: u64,
    pub preview: String,
    pub matches: Vec<String>,
}

#[derive(serde::Deserialize)]
pub struct CommitPayload {
    pub thread_uuid: String,
    pub target_filename: String,
    pub content: String,
}

#[derive(Clone, serde::Serialize)]
pub struct RevisionEvent {
    pub thread_uuid: String,
    pub target_filename: String,
    pub commit_hash: String,
}

#[derive(serde::Deserialize)]
pub struct ContextSyncPayload {
    pub thread_id: String,
    pub content: String,
}

#[derive(serde::Deserialize)]
pub struct GeminiSyncPayload {
    pub url: String,
    pub body: String,
}

#[derive(Clone)]
pub struct CachedThreadInfo {
    pub mtime: u64,
    pub size: u64,
    pub project_path: Option<String>,
    pub title: String,
    pub snippet: String,
    pub parsed_timestamp: u64,
}
