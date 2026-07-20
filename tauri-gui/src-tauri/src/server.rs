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
    AppState, ContextSyncPayload, CommitPayload, ExecutionPayload, GeminiSyncPayload,
    RevisionEvent, SkillItem,
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

async fn handle_skills_list(
) -> Result<Json<Vec<SkillItem>>, (axum::http::StatusCode, String)> {
    let list = vec![
        SkillItem {
            name: "Brainstorming (Phase 0)".to_string(),
            description: "Explore the edges of this idea conceptually".to_string(),
            prompt: "Act as a technical sounding board. I have an idea for a new feature/project, and we need to brainstorm. \n\nDo not try to build it, write code, or structure a final plan yet. Your goal is to help me explore the edges of this idea. Ask me clarifying questions about the core problem, the ideal user experience, and potential pitfalls. Let's keep the conversation fluid and conceptual until I tell you we are ready to lock in a plan.\n\nHere is my initial thought: ".to_string(),
        },
        SkillItem {
            name: "High-Level Plan (Phase 1)".to_string(),
            description: "Synthesize agreed concept into non-technical product map".to_string(),
            prompt: "Act as a Product Manager. We are closing the brainstorming phase. Synthesize our agreed-upon concept into a strict High-Level Plan outlining what this feature DOES and the exact user experience. \n\nStrictly avoid discussing how it is built under the hood. Structure your response using this exact framework:\n1. The Trigger: How the user or system initiates the action.\n2. The Staging Area: The intermediate UI, choices, or routing that happens before execution.\n3. Task Configuration: The rules, modes, or constraints applied to the task.\n4. Execution & Feedback: What happens during the process and how the user knows it finished.".to_string(),
        },
        SkillItem {
            name: "Lower-Level Plan (Phase 2)".to_string(),
            description: "Translate high-level plan into technical architecture".to_string(),
            prompt: "Act as a Systems Architect. Translate our approved High-Level Plan into a Lower-Level Technical Plan. \n\nFocus on the plumbing and architecture. You may include hyper-specific, uncommon code snippets if they are necessary to illustrate an architectural choice (e.g., a specific Rust/Tauri bridge implementation or complex API endpoint), but do not write the standard implementation logic.\n\nBreak down the architecture into:\n1. Tech Stack & CLI Tools: Required packages or background processes.\n2. Component Bridge: How the layers communicate (e.g., file watchers, HTTP, standard I/O).\n3. State & Context Management: Where temporary data or files live during execution.\n4. Technical Bottlenecks: Highlight 2-3 edge cases or potential fail states to watch out for.".to_string(),
        },
        SkillItem {
            name: "Execution Payload (Phase 3)".to_string(),
            description: "Generate strict instruction set for local agent".to_string(),
            prompt: "Act as a Prompt Engineer. We are ready to execute. Take the High-Level Plan and the Lower-Level Technical Plan and generate a strict, optimized instruction set for a local autonomous AI agent.\n\nOutput the final instructions inside a single code block formatted like this:\n```claude-instruction\n[Instructions here]\n```\n\nThe instructions must include:\n- The target context or directory behavior.\n- Strict constraints for the task (e.g., required logging formats, restricted commands).\n- A definitive, step-by-step implementation checklist.\n\nDo not include any conversational filler before or after the code block.".to_string(),
        },
        SkillItem {
            name: "Worker Bee Rules".to_string(),
            description: "Rules for direct coding contributions".to_string(),
            prompt: "Worker Bee Mode: Please execute direct code implementations matching the workspace constraints and rule set.".to_string(),
        },
        SkillItem {
            name: "Triage Rules".to_string(),
            description: "Rules for architectural planning and dispatching".to_string(),
            prompt: "Triage Mode: Please analyze the prompt, deconstruct the task, and prepare delegated sub-tasks rather than executing directly.".to_string(),
        },
    ];
    Ok(Json(list))
}

async fn handle_payload_execute(
    AxumState(app_handle): AxumState<tauri::AppHandle>,
    Json(payload): Json<ExecutionPayload>,
) -> Result<String, (axum::http::StatusCode, String)> {
    println!(
        "Received execution payload for thread: {}",
        payload.thread_id
    );

    let state = app_handle.state::<AppState>();
    if let Ok(mut staged) = state.staged_payload.lock() {
        *staged = Some(payload.clone());
    } else {
        return Err((
            axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            "Failed to lock staged payload".to_string(),
        ));
    }

    let app_handle_clone = app_handle.clone();
    tauri::async_runtime::spawn(async move {
        if let Some(win) = app_handle_clone.get_window("staging-overlay") {
            let _ = win.show();
            let _ = win.set_focus();
            let _ = win.emit("load-payload", payload);
        } else {
            let win_builder = tauri::WindowBuilder::new(
                &app_handle_clone,
                "staging-overlay",
                tauri::WindowUrl::App("staging.html".into()),
            )
            .title("AI-OS: Stage Execution")
            .inner_size(680.0, 420.0)
            .resizable(false)
            .decorations(false)
            .transparent(true)
            .always_on_top(true)
            .center();

            if let Ok(win) = win_builder.build() {
                let payload_clone = payload.clone();
                std::thread::spawn(move || {
                    std::thread::sleep(std::time::Duration::from_millis(500));
                    let _ = win.emit("load-payload", payload_clone);
                });
            }
        }
    });

    Ok("Staged successfully".to_string())
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
            .route("/api/payload/execute", post(handle_payload_execute))
            .route("/api/skills/list", axum::routing::get(handle_skills_list))
            .layer(cors)
            .with_state(app_handle);

        let listener = tokio::net::TcpListener::bind("127.0.0.1:3031")
            .await
            .unwrap();
        axum::serve(listener, app).await.unwrap();
    });
}
