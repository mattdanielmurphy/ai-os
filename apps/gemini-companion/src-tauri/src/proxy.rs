use axum::{extract::State, Json, response::IntoResponse};
use serde::{Deserialize, Serialize};
use crate::{fs_bridge, shell_bridge, context_snapshot};

#[derive(Deserialize)]
struct ExecuteRequest {
    command: String,
    params: String,
}

pub async fn handle_bridge_context(State(root): State<String>) -> impl IntoResponse {
    match context_snapshot::get_project_snapshot(&root) {
        Ok(snapshot) => snapshot,
        Err(e) => format!("Error: {}", e),
    }
}

pub async fn handle_bridge_execute(Json(req): Json<ExecuteRequest>) -> impl IntoResponse {
    // Basic routing logic
    format!("Executing {}", req.command)
}
