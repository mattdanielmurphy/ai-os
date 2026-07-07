use portable_pty::{CommandBuilder, MasterPty, NativePtySystem, PtySize, PtySystem};
use std::io::{Read, Write};
use std::sync::{Arc, Mutex};
use std::collections::HashMap;
use tauri::{Manager, GlobalShortcutManager};
use axum::{
    routing::post,
    Router,
    Json,
    extract::State,
};
use tower_http::cors::{CorsLayer, Any};

// Project session containing its own PTY channels and shell process details
#[allow(dead_code)]
struct ProjectSession {
    claude_writer: Option<Box<dyn Write + Send>>,
    claude_master: Option<Box<dyn MasterPty + Send>>,
    claude_pid: Option<u32>,
    agy_writer: Option<Box<dyn Write + Send>>,
    agy_master: Option<Box<dyn MasterPty + Send>>,
    agy_pid: Option<u32>,
    mini_writer: Box<dyn Write + Send>,
    mini_master: Box<dyn MasterPty + Send>,
    mini_pid: u32,
    project_path: String,
    thread_id: String,
    last_accessed: std::time::SystemTime,
}

#[derive(Clone, serde::Serialize, serde::Deserialize)]
struct ExecutionPayload {
    thread_id: String,
    thread_title: String,
    phase: u32,
    payload: String,
    source_url: String,
    security_token: String,
}

struct AppState {
    // Maps project path (canonical absolute path) to its session state
    sessions: Arc<Mutex<HashMap<String, ProjectSession>>>,
    // Tracks currently active project path
    active_project: Arc<Mutex<Option<String>>>,
    // Keep a clone of the app handle to emit events
    app_handle: tauri::AppHandle,
    // Staged execution payload
    staged_payload: Arc<Mutex<Option<ExecutionPayload>>>,
    // Track the last authenticated account to detect logout/login changes
    last_active_account: Arc<Mutex<Option<String>>>,
}

#[derive(Clone, serde::Serialize)]
struct Payload {
    data: String,
    project_path: String,
    terminal_type: String,
}



#[derive(serde::Deserialize)]
struct CommitPayload {
    thread_uuid: String,
    target_filename: String,
    content: String,
}

#[derive(Clone, serde::Serialize)]
struct RevisionEvent {
    thread_uuid: String,
    target_filename: String,
    commit_hash: String,
}

#[derive(serde::Deserialize)]
struct ContextSyncPayload {
    thread_id: String,
    content: String,
}

async fn handle_sync(
    Json(payload): Json<ContextSyncPayload>,
) -> Result<String, (axum::http::StatusCode, String)> {
    let project_root = std::env::var("AIOS_INITIAL_PROJECT")
        .unwrap_or_else(|_| {
            let cwd = std::env::current_dir().unwrap();
            if cwd.ends_with("src-tauri") {
                cwd.parent().unwrap().to_string_lossy().to_string()
            } else {
                cwd.to_string_lossy().to_string()
            }
        });
        
    println!("Received sync payload for thread {} in root {}", payload.thread_id, project_root);
    
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
    State(app_handle): State<tauri::AppHandle>,
    Json(payload): Json<CommitPayload>,
) -> Result<String, (axum::http::StatusCode, String)> {
    let project_root = std::env::var("AIOS_INITIAL_PROJECT")
        .unwrap_or_else(|_| std::env::current_dir().unwrap().to_string_lossy().to_string());
    
    let log_dir = std::path::Path::new(&project_root)
        .join(".agent-logs")
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
    
    app_handle.emit_all("revision-commit", RevisionEvent {
        thread_uuid: payload.thread_uuid,
        target_filename: payload.target_filename,
        commit_hash,
    }).ok();

    Ok("Commit OK".to_string())
}

#[derive(serde::Deserialize)]
struct GeminiSyncPayload {
    url: String,
    body: String,
}

async fn handle_gemini_sync(
    Json(payload): Json<GeminiSyncPayload>,
) -> Result<String, (axum::http::StatusCode, String)> {
    let project_root = std::env::var("AIOS_INITIAL_PROJECT")
        .unwrap_or_else(|_| {
            let cwd = std::env::current_dir().unwrap();
            if cwd.ends_with("src-tauri") {
                cwd.parent().unwrap().to_string_lossy().to_string()
            } else {
                cwd.to_string_lossy().to_string()
            }
        });
        
    println!("Received gemini sync payload for url {} in root {}", payload.url, project_root);
    
    let log_dir = std::path::Path::new(&project_root)
        .join("gemini-history")
        .join("userscript_logs");
        
    std::fs::create_dir_all(&log_dir)
        .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;
        
    let timestamp = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_millis();
    let file_path = log_dir.join(format!("gemini_sync_{}.json", timestamp));
    
    let content = serde_json::json!({
        "timestamp": timestamp,
        "url": payload.url,
        "body": payload.body
    });
    
    std::fs::write(&file_path, serde_json::to_string_pretty(&content).unwrap())
        .map_err(|e| (axum::http::StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;
        
    Ok("Sync OK".to_string())
}

#[derive(serde::Serialize)]
struct SkillItem {
    name: String,
    description: String,
    prompt: String,
}

async fn handle_skills_list() -> Result<Json<Vec<SkillItem>>, (axum::http::StatusCode, String)> {
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
    State(app_handle): State<tauri::AppHandle>,
    Json(payload): Json<ExecutionPayload>,
) -> Result<String, (axum::http::StatusCode, String)> {
    println!("Received execution payload for thread: {}", payload.thread_id);
    
    let state = app_handle.state::<AppState>();
    if let Ok(mut staged) = state.staged_payload.lock() {
        *staged = Some(payload.clone());
    } else {
        return Err((axum::http::StatusCode::INTERNAL_SERVER_ERROR, "Failed to lock staged payload".to_string()));
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
                tauri::WindowUrl::App("staging.html".into())
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

use axum::extract::ws::{Message, WebSocket, WebSocketUpgrade};
use futures_util::{SinkExt, StreamExt};
use tokio::sync::mpsc;
use std::sync::atomic::{AtomicU64, Ordering};

struct WsState {
    host_tx: Option<mpsc::UnboundedSender<Message>>,
    clients: HashMap<String, mpsc::UnboundedSender<Message>>,
}

static WS_STATE: std::sync::OnceLock<std::sync::Mutex<WsState>> = std::sync::OnceLock::new();
static CLIENT_ID_COUNTER: AtomicU64 = AtomicU64::new(1);

fn get_ws_state() -> &'static std::sync::Mutex<WsState> {
    WS_STATE.get_or_init(|| {
        std::sync::Mutex::new(WsState {
            host_tx: None,
            clients: HashMap::new(),
        })
    })
}

async fn ws_handler(ws: WebSocketUpgrade) -> impl axum::response::IntoResponse {
    ws.on_upgrade(handle_socket)
}

async fn handle_socket(socket: WebSocket) {
    let (mut sender, mut receiver) = socket.split();
    let (tx, mut rx) = mpsc::unbounded_channel::<Message>();

    let my_client_id = format!("client_{}", CLIENT_ID_COUNTER.fetch_add(1, Ordering::SeqCst));
    let client_id_clone = my_client_id.clone();

    let mut write_task = tokio::spawn(async move {
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
                                state.clients.insert(my_client_id.clone(), tx.clone());
                            }
                        }
                        "invoke" => {
                            let mut payload = val.clone();
                            payload["client_id"] = serde_json::Value::String(my_client_id.clone());
                            let forward_msg = Message::Text(payload.to_string().into());
                            let state = get_ws_state().lock().unwrap();
                            if let Some(host_tx) = &state.host_tx {
                                        let _ = host_tx.send(forward_msg);
                            }
                        }
                        "invoke_result" => {
                            if let Some(target_client_id) = val["client_id"].as_str() {
                                let state = get_ws_state().lock().unwrap();
                                if let Some(client_tx) = state.clients.get(target_client_id) {
                                    let _ = client_tx.send(Message::Text(val.to_string().into()));
                                }
                            }
                        }
                        "event" => {
                            let state = get_ws_state().lock().unwrap();
                            let msg_text = val.to_string();
                            for client_tx in state.clients.values() {
                                let _ = client_tx.send(Message::Text(msg_text.clone().into()));
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

fn spawn_axum_server(app_handle: tauri::AppHandle) {
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

        let listener = tokio::net::TcpListener::bind("127.0.0.1:3031").await.unwrap();
        axum::serve(listener, app).await.unwrap();
    });
}

fn is_tmux_available() -> bool {
    static AVAILABLE: std::sync::OnceLock<bool> = std::sync::OnceLock::new();
    *AVAILABLE.get_or_init(|| {
        std::process::Command::new("tmux")
            .arg("-V")
            .output()
            .map(|o| o.status.success())
            .unwrap_or(false)
    })
}

fn has_tmux_session(session_name: &str) -> bool {
    std::process::Command::new("tmux")
        .args(&["-u", "has-session", "-t", session_name])
        .status()
        .map(|s| s.success())
        .unwrap_or(false)
}

fn get_tmux_session_name(project_path: &str, terminal_type: &str, thread_id: Option<&str>) -> String {
    if terminal_type == "mini" {
        let sanitized: String = project_path
            .chars()
            .map(|c| if c.is_alphanumeric() { c } else { '_' })
            .collect();
        format!("ai_os_{}_{}", terminal_type, sanitized.trim_matches('_'))
    } else {
        if let Some(tid) = thread_id {
            if !tid.is_empty() {
                return format!("ai_os_{}_{}", terminal_type, tid);
            }
        }
        format!("ai_os_{}", terminal_type)
    }
}


fn get_tmux_pane_pid(session_name: &str) -> Option<u32> {
    let output = std::process::Command::new("tmux")
        .args(&["list-panes", "-t", session_name, "-F", "#{pane_pid}"])
        .output()
        .ok()?;
    if !output.status.success() {
        return None;
    }
    let stdout = String::from_utf8_lossy(&output.stdout);
    stdout.trim().parse::<u32>().ok()
}

fn is_engine_running_proc(engine: &str, project_path: &str, thread_id: Option<&str>, shell_pid: Option<u32>) -> bool {
    let root_pid = if is_tmux_available() {
        let session_name = get_tmux_session_name(project_path, engine, thread_id);
        if !has_tmux_session(&session_name) {
            return false;
        }
        match get_tmux_pane_pid(&session_name) {
            Some(pid) => pid,
            None => return false,
        }
    } else {
        match shell_pid {
            Some(pid) => pid,
            None => return false,
        }
    };

    let output = match std::process::Command::new("ps")
        .args(&["-A", "-o", "ppid,pid,args"])
        .output() {
            Ok(o) => o,
            Err(_) => return false,
        };
    let stdout = String::from_utf8_lossy(&output.stdout);
    
    let mut parent_to_children: std::collections::HashMap<u32, Vec<u32>> = std::collections::HashMap::new();
    let mut pid_to_args: std::collections::HashMap<u32, String> = std::collections::HashMap::new();
    
    for line in stdout.lines().skip(1) {
        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.len() >= 3 {
            if let (Ok(ppid), Ok(pid)) = (parts[0].parse::<u32>(), parts[1].parse::<u32>()) {
                let args = parts[2..].join(" ");
                parent_to_children.entry(ppid).or_default().push(pid);
                pid_to_args.insert(pid, args);
            }
        }
    }
    
    let mut queue = vec![root_pid];
    let mut visited = std::collections::HashSet::new();
    
    while let Some(current_pid) = queue.pop() {
        if !visited.insert(current_pid) {
            continue;
        }
        if let Some(args) = pid_to_args.get(&current_pid) {
            let args_lower = args.to_lowercase();
            if engine == "claude" {
                if args_lower.contains("claude") {
                    return true;
                }
            } else if engine == "agy" {
                if args_lower.contains("agy") {
                    return true;
                }
            }
        }
        if let Some(children) = parent_to_children.get(&current_pid) {
            for &child in children {
                queue.push(child);
            }
        }
    }
    
    false
}

fn trigger_tmux_refresh(_project_path: &str, _engine: &str) {
    if is_tmux_available() {
        std::thread::spawn(move || {
            std::thread::sleep(std::time::Duration::from_millis(200));
            let _ = std::process::Command::new("tmux")
                .args(&["-u", "refresh-client"])
                .status();
        });
    }
}

// Spawns a single PTY session
fn spawn_single_pty(
    project_path: &str,
    terminal_type: &str,
    app_handle: &tauri::AppHandle,
    thread_id: Option<&str>,
) -> Result<(Box<dyn Write + Send>, Box<dyn MasterPty + Send>, u32, bool), String> {
    let pty_system = NativePtySystem::default();
    let pair = pty_system.openpty(PtySize {
        rows: 24,
        cols: 80,
        pixel_width: 0,
        pixel_height: 0,
    }).map_err(|e| e.to_string())?;

    let mut is_new_tmux = false;
    let mut cmd = if is_tmux_available() {
        let session_name = get_tmux_session_name(project_path, terminal_type, thread_id);
        println!("[DEBUG] tmux is available. Checking for session: {}", session_name);
        if !has_tmux_session(&session_name) {
            println!("[DEBUG] Session {} does not exist. It will be new.", session_name);
            is_new_tmux = true;
        } else {
            println!("[DEBUG] Session {} already exists. Attaching.", session_name);
        }
        let mut c = CommandBuilder::new("tmux");
        let mut args = vec!["-u".to_string(), "new-session".to_string(), "-A".to_string(), "-s".to_string(), session_name.clone(), "-c".to_string(), project_path.to_string()];
        if terminal_type == "claude" {
            args.push("claude --dangerously-skip-permissions".to_string());
        } else if terminal_type == "agy" {
            args.push(format!("agy --add-dir={} --dangerously-skip-permissions", project_path));
        }
        println!("[DEBUG] tmux args: {:?}", args);
        c.args(&args);

        if is_new_tmux {
            let session_name_clone = session_name.clone();
            std::thread::spawn(move || {
                std::thread::sleep(std::time::Duration::from_millis(150));
                let _ = std::process::Command::new("tmux")
                    .args(&["-u", "set-option", "-t", &session_name_clone, "status", "off"])
                    .status();
                let _ = std::process::Command::new("tmux")
                    .args(&["-u", "set-option", "-s", "copy-command", "pbcopy"])
                    .status();
            });
        }
        c
    } else {
        is_new_tmux = true;
        if terminal_type == "claude" {
            let mut c = CommandBuilder::new("claude");
            c.args(&["--dangerously-skip-permissions"]);
            c.cwd(project_path);
            c
        } else if terminal_type == "agy" {
            let mut c = CommandBuilder::new("agy");
            c.args(&["--add-dir", project_path, "--dangerously-skip-permissions"]);
            c.cwd(project_path);
            c
        } else {
            let mut c = CommandBuilder::new("/bin/zsh");
            c.cwd(project_path);
            c
        }
    };

    cmd.env("LANG", "en_US.UTF-8");
    cmd.env("LC_ALL", "en_US.UTF-8");
    cmd.env("TERM", "xterm-256color");

    println!("[DEBUG] Spawning command for project={}, type={}", project_path, terminal_type);
    let _child = pair.slave.spawn_command(cmd).map_err(|e| {
        println!("[DEBUG] Failed to spawn command: {}", e);
        e.to_string()
    })?;
    let shell_pid = _child.process_id().unwrap_or(0);
    println!("[DEBUG] Spawned command with shell_pid={}", shell_pid);

    let reader = pair.master.try_clone_reader().map_err(|e| {
        println!("[DEBUG] Failed to clone reader: {}", e);
        e.to_string()
    })?;
    let writer = pair.master.take_writer().map_err(|e| {
        println!("[DEBUG] Failed to take writer: {}", e);
        e.to_string()
    })?;

    // Spawn reader thread for this specific PTY
    let app_handle_clone = app_handle.clone();
    let path_clone = project_path.to_string();
    let type_clone = terminal_type.to_string();
    std::thread::spawn(move || {
        let mut reader = reader;
        let mut buf = [0u8; 1024];
        let mut leftover = Vec::new();
        loop {
            match reader.read(&mut buf) {
                Ok(n) if n > 0 => {
                    leftover.extend_from_slice(&buf[..n]);
                    let mut valid_len = leftover.len();
                    
                    while valid_len > 0 {
                        match std::str::from_utf8(&leftover[..valid_len]) {
                            Ok(_) => break,
                            Err(e) => {
                                if e.error_len().is_none() {
                                    valid_len = e.valid_up_to();
                                } else {
                                    valid_len = e.valid_up_to();
                                    break;
                                }
                            }
                        }
                    }
                    
                    if valid_len == 0 && !leftover.is_empty() {
                        if leftover.len() >= 4 {
                            valid_len = leftover.len();
                        }
                    }

                    if valid_len > 0 {
                        let data = String::from_utf8_lossy(&leftover[..valid_len]).to_string();
                        leftover.drain(..valid_len);
                        app_handle_clone.emit_all("pty-output", Payload {
                            data,
                            project_path: path_clone.clone(),
                            terminal_type: type_clone.clone(),
                        }).ok();
                    }
                }
                _ => break,
            }
        }
    });

    Ok((writer, pair.master, shell_pid, is_new_tmux))
}

fn is_process_alive(pid: u32) -> bool {
    std::process::Command::new("kill")
        .args(&["-0", &pid.to_string()])
        .status()
        .map(|s| s.success())
        .unwrap_or(false)
}

fn ensure_engine_pty(
    project_path: &str,
    engine: &str,
    app_handle: &tauri::AppHandle,
    session: &mut ProjectSession,
) -> Result<(u32, bool), String> {
    let thread_id_opt = if session.thread_id.is_empty() { None } else { Some(session.thread_id.as_str()) };
    if engine == "claude" {
        let mut agy_alive = false;
        let mut client_alive = false;
        if let Some(pid) = session.claude_pid {
            agy_alive = is_engine_running_proc("claude", project_path, thread_id_opt, session.claude_pid);
            client_alive = is_process_alive(pid);
        }
        if !agy_alive || !client_alive {
            if is_tmux_available() && !agy_alive {
                let session_name = get_tmux_session_name(project_path, "claude", thread_id_opt);
                if has_tmux_session(&session_name) {
                    let _ = std::process::Command::new("tmux")
                        .args(&["kill-session", "-t", &session_name])
                        .status();
                }
            }
            let (writer, master, pid, is_new) = spawn_single_pty(project_path, "claude", app_handle, thread_id_opt)?;
            session.claude_writer = Some(writer);
            session.claude_master = Some(master);
            session.claude_pid = Some(pid);
            Ok((pid, is_new))
        } else {
            Ok((session.claude_pid.unwrap(), false))
        }
    } else if engine == "agy" {
        let mut agy_alive = false;
        let mut client_alive = false;
        if let Some(pid) = session.agy_pid {
            agy_alive = is_engine_running_proc("agy", project_path, thread_id_opt, session.agy_pid);
            client_alive = is_process_alive(pid);
        }
        if !agy_alive || !client_alive {
            if is_tmux_available() && !agy_alive {
                let session_name = get_tmux_session_name(project_path, "agy", thread_id_opt);
                if has_tmux_session(&session_name) {
                    let _ = std::process::Command::new("tmux")
                        .args(&["kill-session", "-t", &session_name])
                        .status();
                }
            }
            let (writer, master, pid, is_new) = spawn_single_pty(project_path, "agy", app_handle, thread_id_opt)?;
            session.agy_writer = Some(writer);
            session.agy_master = Some(master);
            session.agy_pid = Some(pid);
            Ok((pid, is_new))
        } else {
            Ok((session.agy_pid.unwrap(), false))
        }
    } else {
        Err(format!("Unknown engine: {}", engine))
    }
}

fn ensure_mini_pty(
    project_path: &str,
    app_handle: &tauri::AppHandle,
    session: &mut ProjectSession,
) -> Result<(), String> {
    if !is_process_alive(session.mini_pid) {
        let (writer, master, pid, _) = spawn_single_pty(project_path, "mini", app_handle, None)?;
        session.mini_writer = writer;
        session.mini_master = master;
        session.mini_pid = pid;
    }
    Ok(())
}

#[derive(Clone, serde::Serialize)]
struct SwitchResult {
    shell_pid: u32,
    is_new_session: bool,
}

#[tauri::command]
fn prepare_spare_engine(project_path: String, engine: String) -> Result<(), String> {
    if !is_tmux_available() {
        return Ok(());
    }
    let spare_session = format!("{}_spare", get_tmux_session_name(&project_path, &engine, None));
    if has_tmux_session(&spare_session) {
        return Ok(());
    }

    let project_path_clone = project_path.clone();
    let engine_clone = engine.clone();
    std::thread::spawn(move || {
        let mut args = vec![
            "-u".to_string(),
            "new-session".to_string(),
            "-d".to_string(),
            "-s".to_string(),
            spare_session.clone(),
            "-c".to_string(),
            project_path_clone.clone(),
        ];
        if engine_clone == "claude" {
            args.push("claude --dangerously-skip-permissions".to_string());
        } else if engine_clone == "agy" {
            args.push(format!("agy --add-dir={} --dangerously-skip-permissions", project_path_clone));
        }

        let _ = std::process::Command::new("tmux")
            .args(&args)
            .status();

        std::thread::sleep(std::time::Duration::from_millis(150));
        let _ = std::process::Command::new("tmux")
            .args(&["-u", "set-option", "-t", &spare_session, "status", "off"])
            .status();
        let _ = std::process::Command::new("tmux")
            .args(&["-u", "set-option", "-s", "copy-command", "pbcopy"])
            .status();
    });

    Ok(())
}

#[tauri::command]
fn spawn_fresh_engine(
    project_path: String,
    engine: String,
    thread_id: Option<String>,
    state: tauri::State<AppState>,
) -> Result<u32, String> {
    let app_handle = state.app_handle.clone();
    let thread_id_str = thread_id.unwrap_or_default();
    let session_key = format!("{}_{}", project_path, thread_id_str);

    let mut sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    let session = sessions.get_mut(&session_key).ok_or_else(|| "No session found".to_string())?;

    let thread_id_opt = if session.thread_id.is_empty() { None } else { Some(session.thread_id.as_str()) };

    if is_tmux_available() {
        let session_name = get_tmux_session_name(&project_path, &engine, thread_id_opt);
        let spare_session = format!("ai_os_{}_spare", engine);

        if has_tmux_session(&spare_session) {
            if has_tmux_session(&session_name) {
                let _ = std::process::Command::new("tmux")
                    .args(&["kill-session", "-t", &session_name])
                    .status();
            }
            let _ = std::process::Command::new("tmux")
                .args(&["rename-session", "-t", &spare_session, &session_name])
                .status();
        } else {
            if has_tmux_session(&session_name) {
                let _ = std::process::Command::new("tmux")
                    .args(&["kill-session", "-t", &session_name])
                    .status();
            }
        }
    }

    let (writer, master, pid, _) = spawn_single_pty(&project_path, &engine, &app_handle, thread_id_opt)?;
    if engine == "claude" {
        session.claude_writer = Some(writer);
        session.claude_master = Some(master);
        session.claude_pid = Some(pid);
    } else if engine == "agy" {
        session.agy_writer = Some(writer);
        session.agy_master = Some(master);
        session.agy_pid = Some(pid);
    }

    trigger_tmux_refresh(&project_path, &engine);
    
    let path_clone = project_path.clone();
    let engine_clone = engine.clone();
    std::thread::spawn(move || {
        let _ = prepare_spare_engine(path_clone, engine_clone);
    });

    Ok(pid)
}

#[tauri::command]
fn initialize_project_session(project_path: String, thread_id: Option<String>, state: tauri::State<AppState>) -> Result<u32, String> {
    let app_handle = state.app_handle.clone();
    let thread_id_str = thread_id.unwrap_or_default();
    let session_key = format!("{}_{}", project_path, thread_id_str);

    let mut sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    if !sessions.contains_key(&session_key) {
        let (mini_writer, mini_master, mini_pid, _) = spawn_single_pty(&project_path, "mini", &app_handle, None)?;
        sessions.insert(
            session_key.clone(),
            ProjectSession {
                claude_writer: None,
                claude_master: None,
                claude_pid: None,
                agy_writer: None,
                agy_master: None,
                agy_pid: None,
                mini_writer,
                mini_master,
                mini_pid,
                project_path: project_path.clone(),
                thread_id: thread_id_str.clone(),
                last_accessed: std::time::SystemTime::now(),
            },
        );
    }
    let session = sessions.get_mut(&session_key).unwrap();
    session.last_accessed = std::time::SystemTime::now();
    let (pid, _) = ensure_engine_pty(&project_path, "agy", &app_handle, session)?;
    Ok(pid)
}

#[tauri::command]
fn switch_active_project(project_path: String, engine: String, thread_id: Option<String>, state: tauri::State<AppState>) -> Result<SwitchResult, String> {
    let app_handle = state.app_handle.clone();
    let thread_id_str = thread_id.unwrap_or_default();
    let session_key = format!("{}_{}", project_path, thread_id_str);

    let mut sessions = state.sessions.lock().map_err(|e| e.to_string())?;

    // Evict old sessions if we have too many
    if sessions.len() >= 20 && !sessions.contains_key(&session_key) {
        let mut keys_to_evict = Vec::new();
        let mut sorted_sessions: Vec<_> = sessions.iter().map(|(k, s)| (k.clone(), s.last_accessed)).collect();
        sorted_sessions.sort_by_key(|&(_, t)| t);
        
        let num_to_evict = (sessions.len() - 15).min(sorted_sessions.len());
        for i in 0..num_to_evict {
            keys_to_evict.push(sorted_sessions[i].0.clone());
        }
        
        for k in keys_to_evict {
            if let Some(mut old_session) = sessions.remove(&k) {
                if let Some(pid) = old_session.claude_pid {
                    let _ = std::process::Command::new("kill").arg("-9").arg(pid.to_string()).status();
                }
                if let Some(pid) = old_session.agy_pid {
                    let _ = std::process::Command::new("kill").arg("-9").arg(pid.to_string()).status();
                }
                let _ = std::process::Command::new("kill").arg("-9").arg(old_session.mini_pid.to_string()).status();
                
                if is_tmux_available() {
                    let thread_id_opt = if old_session.thread_id.is_empty() { None } else { Some(old_session.thread_id.as_str()) };
                    let cl_session = get_tmux_session_name(&old_session.project_path, "claude", thread_id_opt);
                    let ag_session = get_tmux_session_name(&old_session.project_path, "agy", thread_id_opt);
                    let mi_session = get_tmux_session_name(&old_session.project_path, "mini", None);
                    
                    let _ = std::process::Command::new("tmux").args(&["-u", "kill-session", "-t", &cl_session]).status();
                    let _ = std::process::Command::new("tmux").args(&["-u", "kill-session", "-t", &ag_session]).status();
                    let _ = std::process::Command::new("tmux").args(&["-u", "kill-session", "-t", &mi_session]).status();
                }
            }
        }
    }

    let is_new_proj = !sessions.contains_key(&session_key);
    if is_new_proj {
        // Spawn mini and engine PTYs in parallel to speed up tab loading
        let app_handle_clone1 = app_handle.clone();
        let app_handle_clone2 = app_handle.clone();
        let path_clone1 = project_path.clone();
        let path_clone2 = project_path.clone();
        let engine_clone = engine.clone();
        let thread_id_clone1 = thread_id_str.clone();

        let mini_thread = std::thread::spawn(move || {
            spawn_single_pty(&path_clone1, "mini", &app_handle_clone1, None)
        });
        let engine_thread = std::thread::spawn(move || {
            let thread_id_opt = if thread_id_clone1.is_empty() { None } else { Some(thread_id_clone1.as_str()) };
            spawn_single_pty(&path_clone2, &engine_clone, &app_handle_clone2, thread_id_opt)
        });

        let (mini_writer, mini_master, mini_pid, _) = mini_thread.join()
            .map_err(|_| "Failed to join mini PTY spawn thread".to_string())??;
        let (engine_writer, engine_master, engine_pid, is_new_session) = engine_thread.join()
            .map_err(|_| "Failed to join engine PTY spawn thread".to_string())??;

        let mut session = ProjectSession {
            claude_writer: None,
            claude_master: None,
            claude_pid: None,
            agy_writer: None,
            agy_master: None,
            agy_pid: None,
            mini_writer,
            mini_master,
            mini_pid,
            project_path: project_path.clone(),
            thread_id: thread_id_str.clone(),
            last_accessed: std::time::SystemTime::now(),
        };

        if engine == "claude" {
            session.claude_writer = Some(engine_writer);
            session.claude_master = Some(engine_master);
            session.claude_pid = Some(engine_pid);
        } else if engine == "agy" {
            session.agy_writer = Some(engine_writer);
            session.agy_master = Some(engine_master);
            session.agy_pid = Some(engine_pid);
        }

        sessions.insert(session_key.clone(), session);

        let mut active = state.active_project.lock().map_err(|e| e.to_string())?;
        *active = Some(project_path.clone());

        trigger_tmux_refresh(&project_path, &engine);

        return Ok(SwitchResult {
            shell_pid: engine_pid,
            is_new_session,
        });
    }

    let session = sessions.get_mut(&session_key).unwrap();
    session.last_accessed = std::time::SystemTime::now();
    let (shell_pid, is_new_session) = ensure_engine_pty(&project_path, &engine, &app_handle, session)?;
    ensure_mini_pty(&project_path, &app_handle, session)?;

    let mut active = state.active_project.lock().map_err(|e| e.to_string())?;
    *active = Some(project_path.clone());

    trigger_tmux_refresh(&project_path, &engine);

    Ok(SwitchResult {
        shell_pid,
        is_new_session,
    })
}

#[tauri::command]
fn write_to_pty(data: String, project_path: String, terminal_type: String, thread_id: Option<String>, state: tauri::State<AppState>) -> Result<(), String> {
    let thread_id_str = thread_id.unwrap_or_default();
    let session_key = format!("{}_{}", project_path, thread_id_str);

    let mut sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    if let Some(session) = sessions.get_mut(&session_key) {
        let writer = if terminal_type == "mini" {
            Some(&mut session.mini_writer)
        } else if terminal_type == "claude" {
            session.claude_writer.as_mut()
        } else if terminal_type == "agy" {
            session.agy_writer.as_mut()
        } else {
            None
        };
        if let Some(w) = writer {
            w.write_all(data.as_bytes()).map_err(|e| e.to_string())?;
            w.flush().map_err(|e| e.to_string())?;
            Ok(())
        } else {
            Err(format!("PTY session not initialized for: {}", terminal_type))
        }
    } else {
        Err(format!("No PTY session found for project: {}", project_path))
    }
}

#[tauri::command]
fn resize_pty(rows: u16, cols: u16, project_path: String, terminal_type: String, thread_id: Option<String>, state: tauri::State<AppState>) -> Result<(), String> {
    let thread_id_str = thread_id.unwrap_or_default();
    let session_key = format!("{}_{}", project_path, thread_id_str);

    let sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    if let Some(session) = sessions.get(&session_key) {
        let size = PtySize {
            rows,
            cols,
            pixel_width: 0,
            pixel_height: 0,
        };
        if terminal_type == "mini" {
            session.mini_master.resize(size).map_err(|e| e.to_string())?;
        } else {
            if let Some(ref claude_master) = session.claude_master {
                let _ = claude_master.resize(size);
            }
            if let Some(ref agy_master) = session.agy_master {
                let _ = agy_master.resize(size);
            }
        }
        Ok(())
    } else {
        Err(format!("No PTY session found for project: {}", project_path))
    }
}

#[tauri::command]
fn is_engine_running(engine: String, project_path: String, thread_id: Option<String>, state: tauri::State<AppState>) -> Result<bool, String> {
    let thread_id_str = thread_id.unwrap_or_default();
    let session_key = format!("{}_{}", project_path, thread_id_str);

    let sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    let shell_pid = match sessions.get(&session_key) {
        Some(s) => {
            if engine == "claude" {
                s.claude_pid
            } else {
                s.agy_pid
            }
        }
        None => return Ok(false),
    };
    drop(sessions);

    let thread_id_opt = if thread_id_str.is_empty() { None } else { Some(thread_id_str.as_str()) };
    Ok(is_engine_running_proc(&engine, &project_path, thread_id_opt, shell_pid))
}

fn find_agent_pid(shell_pid: u32) -> Option<u32> {
    let output = std::process::Command::new("ps")
        .args(&["-A", "-o", "ppid,pid,args"])
        .output()
        .ok()?;
    let stdout = String::from_utf8_lossy(&output.stdout);
    
    let mut parent_to_children: std::collections::HashMap<u32, Vec<u32>> = std::collections::HashMap::new();
    let mut pid_to_args: std::collections::HashMap<u32, String> = std::collections::HashMap::new();
    
    for line in stdout.lines().skip(1) {
        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.len() >= 3 {
            if let (Ok(ppid), Ok(pid)) = (parts[0].parse::<u32>(), parts[1].parse::<u32>()) {
                let args = parts[2..].join(" ");
                parent_to_children.entry(ppid).or_default().push(pid);
                pid_to_args.insert(pid, args);
            }
        }
    }
    
    let mut queue = vec![shell_pid];
    let mut visited = std::collections::HashSet::new();
    let mut found_pid = None;
    
    while let Some(current_pid) = queue.pop() {
        if !visited.insert(current_pid) {
            continue;
        }
        if let Some(args) = pid_to_args.get(&current_pid) {
            let args_lower = args.to_lowercase();
            if args_lower.contains("claude") || args_lower.contains("agy") {
                found_pid = Some(current_pid);
                break;
            }
        }
        if let Some(children) = parent_to_children.get(&current_pid) {
            for &child in children {
                queue.push(child);
            }
        }
    }
    
    found_pid.or(Some(shell_pid))
}

fn has_open_write_files(pid: u32) -> bool {
    let output = std::process::Command::new("lsof")
        .args(&["-p", &pid.to_string()])
        .output();
        
    if let Ok(out) = output {
        let stdout = String::from_utf8_lossy(&out.stdout);
        for line in stdout.lines().skip(1) {
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() >= 5 {
                let fd = parts[3];
                let file_type = parts[4];
                if file_type == "REG" && (fd.contains('w') || fd.contains('u')) {
                    return true;
                }
            }
        }
    }
    false
}

fn has_active_network_traffic(pid: u32) -> bool {
    let output = std::process::Command::new("lsof")
        .args(&["-i", "-a", "-p", &pid.to_string()])
        .output();
        
    if let Ok(out) = output {
        let stdout = String::from_utf8_lossy(&out.stdout);
        if stdout.contains("ESTABLISHED") {
            return true;
        }
    }
    false
}

fn has_child_processes(agent_pid: u32) -> bool {
    let output = std::process::Command::new("ps")
        .args(&["-A", "-o", "ppid,pid"])
        .output();
        
    if let Ok(out) = output {
        let stdout = String::from_utf8_lossy(&out.stdout);
        for line in stdout.lines().skip(1) {
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() >= 2 {
                if let Ok(ppid) = parts[0].parse::<u32>() {
                    if ppid == agent_pid {
                        return true;
                    }
                }
            }
        }
    }
    false
}

#[derive(Clone, serde::Serialize)]
struct PauseStatusPayload {
    project_path: String,
    status: String,
}

#[tauri::command]
fn toggle_process_pause(project_path: String, engine: String, pause: bool, thread_id: Option<String>, state: tauri::State<AppState>) -> Result<(), String> {
    let thread_id_str = thread_id.unwrap_or_default();
    let session_key = format!("{}_{}", project_path, thread_id_str);

    let sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    let session = sessions.get(&session_key)
        .ok_or_else(|| format!("No active session for key: {}", session_key))?;
    let shell_pid = if engine == "claude" {
        session.claude_pid
    } else {
        session.agy_pid
    };
    let shell_pid = match shell_pid {
        Some(pid) => pid,
        None => return Err(format!("Engine {} is not running", engine)),
    };
    drop(sessions);

    if shell_pid == 0 {
        return Err("Invalid process ID".to_string());
    }

    if !pause {
        let signal = "-CONT";
        std::process::Command::new("kill")
            .args(&[signal, &shell_pid.to_string()])
            .status()
            .map_err(|e| e.to_string())?;
            
        state.app_handle.emit_all("pause-status", PauseStatusPayload {
            project_path: project_path.clone(),
            status: "Running".to_string(),
        }).ok();
        return Ok(());
    }

    state.app_handle.emit_all("pause-status", PauseStatusPayload {
        project_path: project_path.clone(),
        status: "Pending".to_string(),
    }).ok();

    let app_handle_clone = state.app_handle.clone();
    let project_path_clone = project_path.clone();
    std::thread::spawn(move || {
        loop {
            let agent_pid = match find_agent_pid(shell_pid) {
                Some(pid) => pid,
                None => shell_pid,
            };

            let net_active = has_active_network_traffic(agent_pid);
            let wr_active = has_open_write_files(agent_pid);
            let child_active = has_child_processes(agent_pid);

            if !net_active && !wr_active && !child_active {
                let _ = std::process::Command::new("kill")
                    .args(&["-TSTP", &shell_pid.to_string()])
                    .status();

                app_handle_clone.emit_all("pause-status", PauseStatusPayload {
                    project_path: project_path_clone.clone(),
                    status: "Paused".to_string(),
                }).ok();
                break;
            }

            std::thread::sleep(std::time::Duration::from_millis(50));
        }
    });

    Ok(())
}

#[tauri::command]
fn close_project_session(project_path: String, state: tauri::State<AppState>) -> Result<(), String> {
    let mut sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    let prefix = format!("{}_", project_path);
    let keys_to_remove: Vec<String> = sessions.keys()
        .filter(|k| k.starts_with(&prefix))
        .cloned()
        .collect();
    
    for key in keys_to_remove {
        if let Some(session) = sessions.remove(&key) {
            let thread_id_opt = if session.thread_id.is_empty() { None } else { Some(session.thread_id.as_str()) };
            let cl_session = get_tmux_session_name(&project_path, "claude", thread_id_opt);
            let ag_session = get_tmux_session_name(&project_path, "agy", thread_id_opt);
            let mi_session = get_tmux_session_name(&project_path, "mini", None);
            
            let _ = std::process::Command::new("tmux").args(&["-u", "kill-session", "-t", &cl_session]).status();
            let _ = std::process::Command::new("tmux").args(&["-u", "kill-session", "-t", &ag_session]).status();
            let _ = std::process::Command::new("tmux").args(&["-u", "kill-session", "-t", &mi_session]).status();
        }
    }
    Ok(())
}

#[tauri::command]
async fn select_directory() -> Result<Option<String>, String> {
    let (tx, rx) = std::sync::mpsc::channel();
    tauri::api::dialog::FileDialogBuilder::new().pick_folder(move |path| {
        tx.send(path).ok();
    });
    let path = rx.recv().map_err(|e| e.to_string())?;
    match path {
        Some(path) => Ok(Some(path.to_string_lossy().to_string())),
        None => Ok(None),
    }
}

#[tauri::command]
fn create_new_project(name: String, git_repo_name: String) -> Result<String, String> {
    use std::fs;
    use std::process::Command;
    use std::path::Path;

    let home = std::env::var("HOME").map_err(|_| "Could not find HOME directory".to_string())?;
    let projects_dir = Path::new(&home).join("projects");
    if !projects_dir.exists() {
        fs::create_dir_all(&projects_dir).map_err(|e| format!("Failed to create projects directory: {}", e))?;
    }

    let project_path = projects_dir.join(&name);
    if project_path.exists() {
        return Err("Project directory already exists".to_string());
    }

    fs::create_dir_all(&project_path).map_err(|e| format!("Failed to create project directory: {}", e))?;

    // git init
    let output = Command::new("git")
        .arg("init")
        .current_dir(&project_path)
        .output()
        .map_err(|e| format!("Failed to run git init: {}", e))?;
    if !output.status.success() {
        return Err(format!("git init failed: {}", String::from_utf8_lossy(&output.stderr)));
    }

    // Create README.md
    let readme_content = format!("# {}\n", name);
    fs::write(project_path.join("README.md"), readme_content)
        .map_err(|e| format!("Failed to write README.md: {}", e))?;

    // git add README.md
    let output = Command::new("git")
        .args(&["add", "README.md"])
        .current_dir(&project_path)
        .output()
        .map_err(|e| format!("Failed to run git add: {}", e))?;
    if !output.status.success() {
        return Err(format!("git add failed: {}", String::from_utf8_lossy(&output.stderr)));
    }

    // git commit -m "Initial commit"
    let output = Command::new("git")
        .args(&["commit", "-m", "Initial commit"])
        .current_dir(&project_path)
        .output()
        .map_err(|e| format!("Failed to run git commit: {}", e))?;
    if !output.status.success() {
        return Err(format!("git commit failed: {}", String::from_utf8_lossy(&output.stderr)));
    }

    // gh repo create <git_repo_name> --private --source=. --remote=origin --push
    let output = Command::new("gh")
        .args(&["repo", "create", &git_repo_name, "--private", "--source=.", "--remote=origin", "--push"])
        .current_dir(&project_path)
        .output()
        .map_err(|e| format!("Failed to run gh repo create: {}", e))?;
    if !output.status.success() {
        return Err(format!("gh repo create failed: {}", String::from_utf8_lossy(&output.stderr)));
    }

    Ok(project_path.to_string_lossy().to_string())
}

#[tauri::command]
fn copy_tmux_selection(project_path: String, terminal_type: String, thread_id: Option<String>) -> Result<(), String> {
    if is_tmux_available() {
        let thread_id_opt = thread_id.as_deref();
        let session_name = get_tmux_session_name(&project_path, &terminal_type, thread_id_opt);
        let status = std::process::Command::new("tmux")
            .args(&["-u", "send-keys", "-t", &session_name, "-X", "copy-pipe-and-cancel", "pbcopy"])
            .status();
        match status {
            Ok(s) if s.success() => Ok(()),
            Ok(s) => Err(format!("tmux exited with status: {}", s)),
            Err(e) => Err(e.to_string()),
        }
    } else {
        Err("tmux not available".to_string())
    }
}

#[tauri::command]
fn open_path(path: String) -> Result<(), String> {
    let mut actual_path = path.clone();
    if actual_path.starts_with("~/") {
        if let Ok(home) = std::env::var("HOME") {
            actual_path = actual_path.replacen("~/", &format!("{}/", home), 1);
        }
    }
    std::process::Command::new("open")
        .arg(&actual_path)
        .spawn()
        .map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
fn get_initial_project() -> Option<String> {
    std::env::var("AIOS_INITIAL_PROJECT").ok()
}

#[derive(serde::Serialize, Clone)]
struct ThreadLog {
    id: String,
    latest_leaf_id: String,
    title: String,
    snippet: String,
    filepath: String,
    mtime: u64,
    #[serde(skip_serializing_if = "Option::is_none")]
    detected_project_path: Option<String>,
}

fn get_root_thread_id(thread_id: &str, child_to_parent: &HashMap<String, String>) -> String {
    let mut current = thread_id.to_string();
    let mut visited = std::collections::HashSet::new();
    visited.insert(current.clone());
    while let Some(parent) = child_to_parent.get(&current) {
        if visited.contains(parent) {
            break;
        }
        current = parent.clone();
        visited.insert(current.clone());
    }
    current
}

static CHILD_TO_PARENT_CACHE: std::sync::OnceLock<std::sync::Mutex<HashMap<String, String>>> = std::sync::OnceLock::new();

#[derive(Clone)]
struct CachedThreadInfo {
    mtime: u64,
    size: u64,
    project_path: Option<String>,
    title: String,
    snippet: String,
}

static THREAD_INFO_CACHE: std::sync::OnceLock<std::sync::Mutex<HashMap<String, CachedThreadInfo>>> = std::sync::OnceLock::new();

fn get_child_to_parent_map(brain_dir: &std::path::Path) -> HashMap<String, String> {
    let cache_mutex = CHILD_TO_PARENT_CACHE.get_or_init(|| std::sync::Mutex::new(HashMap::new()));
    let mut cache = cache_mutex.lock().unwrap();

    if let Ok(entries) = std::fs::read_dir(brain_dir) {
        for entry in entries {
            if let Ok(entry) = entry {
                let path = entry.path();
                if path.is_dir() {
                    if let Some(thread_id) = path.file_name().map(|n| n.to_string_lossy().to_string()) {
                        if cache.contains_key(&thread_id) {
                            continue;
                        }
                        let transcript_path = path.join(".system_generated").join("logs").join("transcript.jsonl");
                        if transcript_path.exists() {
                            use std::io::Read;
                            if let Ok(mut file) = std::fs::File::open(&transcript_path) {
                                let mut buffer = vec![0; 4096];
                                if let Ok(n) = file.read(&mut buffer) {
                                    let content = String::from_utf8_lossy(&buffer[..n]);
                                    if let Some(pos) = content.find("Continuing conversation from history (Thread ID:") {
                                        let after = &content[pos + "Continuing conversation from history (Thread ID:".len()..];
                                        if let Some(end_pos) = after.find(')') {
                                            let parent_id = after[..end_pos].trim().to_string();
                                            if parent_id.chars().all(|c| c.is_alphanumeric() || c == '-') {
                                                cache.insert(thread_id.clone(), parent_id);
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    cache.clone()
}

fn scan_brain_threads(brain_dir: &std::path::Path) -> (HashMap<String, String>, HashMap<String, u64>) {
    let child_to_parent = get_child_to_parent_map(brain_dir);
    let mut thread_mtimes = HashMap::new();

    if let Ok(entries) = std::fs::read_dir(brain_dir) {
        for entry in entries {
            if let Ok(entry) = entry {
                let path = entry.path();
                if path.is_dir() {
                    if let Some(thread_id) = path.file_name().map(|n| n.to_string_lossy().to_string()) {
                        let transcript_path = path.join(".system_generated").join("logs").join("transcript.jsonl");
                        if transcript_path.exists() {
                            if let Ok(metadata) = std::fs::metadata(&transcript_path) {
                                let mtime = metadata.modified()
                                    .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e)))
                                    .map(|d| d.as_secs())
                                    .unwrap_or(0);
                                thread_mtimes.insert(thread_id.clone(), mtime);
                            }
                        }
                    }
                }
            }
        }
    }

    (child_to_parent, thread_mtimes)
}

fn get_cached_thread_info(latest_filepath: &std::path::Path, latest_thread_id: &str) -> Option<CachedThreadInfo> {
    let metadata = std::fs::metadata(latest_filepath).ok()?;
    let mtime = metadata.modified()
        .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e)))
        .map(|d| d.as_secs())
        .unwrap_or(0);
    let size = metadata.len();

    let cache_mutex = THREAD_INFO_CACHE.get_or_init(|| std::sync::Mutex::new(HashMap::new()));
    {
        let cache = cache_mutex.lock().unwrap();
        if let Some(info) = cache.get(latest_thread_id) {
            if info.mtime == mtime && info.size == size {
                return Some(info.clone());
            }
        }
    }

    // Cache miss or modified file. Let's read and parse.
    use std::fs;
    use std::io::Read;
    let file = fs::File::open(latest_filepath).ok()?;
    let mut buffer = Vec::new();
    let _ = file.take(131072).read_to_end(&mut buffer);
    let content = String::from_utf8_lossy(&buffer);
    let project_path = detect_project_path(&content);
    let mut title = latest_thread_id.to_string();
    let mut snippet = String::new();

    let mut found_title = false;

    for line in content.lines() {
        if let Ok(obj) = serde_json::from_str::<serde_json::Value>(line) {
            let msg_type = obj.get("type").and_then(|v| v.as_str());
            
            if msg_type == Some("PLANNER_RESPONSE") && !found_title {
                if let Some(content_str) = obj.get("content").and_then(|v| v.as_str()) {
                    if let Some(start_idx) = content_str.find("<THREAD_NAME>") {
                        if let Some(end_idx) = content_str[start_idx..].find("</THREAD_NAME>") {
                            title = content_str[start_idx + 13..start_idx + end_idx].trim().to_string();
                            found_title = true;
                            println!("[DEBUG thread-naming] Extracted title '{}' from PLANNER_RESPONSE in {}", title, latest_thread_id);
                        }
                    }
                }
            }
            
            if msg_type == Some("USER_INPUT") && snippet.is_empty() {
                if let Some(prompt_content) = obj.get("content").and_then(|v| v.as_str()) {
                    let mut raw_prompt = prompt_content.to_string();
                    if let Some(start_idx) = raw_prompt.find("<USER_REQUEST>") {
                        if let Some(end_idx) = raw_prompt.find("</USER_REQUEST>") {
                            raw_prompt = raw_prompt[start_idx + 14..end_idx].trim().to_string();
                        }
                    }
                    
                    if let Some(sys_idx) = raw_prompt.find("<SYSTEM_INSTRUCTIONS>") {
                        raw_prompt = raw_prompt[..sys_idx].trim().to_string();
                    }
                    
                    if raw_prompt.contains("Continuing conversation from history") {
                        if let Some(user_req_idx) = raw_prompt.find("\nUser request:") {
                            raw_prompt = raw_prompt[user_req_idx + "\nUser request:".len()..].trim().to_string();
                        } else if let Some(user_req_idx) = raw_prompt.rfind("User request:") {
                            raw_prompt = raw_prompt[user_req_idx + "User request:".len()..].trim().to_string();
                        }
                    }
                    
                    let clean_prompt = raw_prompt.replace("\r", "").replace("\n", " ");
                    let char_count = clean_prompt.chars().count();
                    
                    if !found_title {
                        title = if char_count > 40 {
                            format!("{}...", clean_prompt.chars().take(40).collect::<String>())
                        } else {
                            clean_prompt.clone()
                        };
                        println!("[DEBUG thread-naming] Fallback title set to '{}' for {}", title, latest_thread_id);
                    }
                    
                    snippet = if char_count > 120 {
                        format!("{}...", clean_prompt.chars().take(30).collect::<String>())
                    } else {
                        clean_prompt
                    };
                    println!("[DEBUG thread-naming] Snippet set for {}", latest_thread_id);
                }
            }
            
            if found_title && !snippet.is_empty() {
                break;
            }
        }
    }

    let info = CachedThreadInfo {
        mtime,
        size,
        project_path,
        title,
        snippet,
    };

    let mut cache = cache_mutex.lock().unwrap();
    cache.insert(latest_thread_id.to_string(), info.clone());
    Some(info)
}

fn get_thread_chain(
    root_id: &str,
    child_to_parent: &HashMap<String, String>,
    thread_mtimes: &HashMap<String, u64>,
) -> Vec<String> {
    let mut chain = Vec::new();
    for thread_id in thread_mtimes.keys() {
        if get_root_thread_id(thread_id, child_to_parent) == root_id {
            chain.push(thread_id.clone());
        }
    }
    chain.sort_by_key(|id| thread_mtimes.get(id).cloned().unwrap_or(0));
    chain
}

#[tauri::command]
fn get_project_threads(project_path: String) -> Result<Vec<ThreadLog>, String> {
    use std::path::Path;

    let home = std::env::var("HOME").map_err(|_| "Could not find HOME directory".to_string())?;
    let brain_dir = Path::new(&home)
        .join(".gemini")
        .join("antigravity-cli")
        .join("brain");

    if !brain_dir.exists() {
        return Ok(Vec::new());
    }

    let is_misc = project_path.ends_with("/projects/Misc") || project_path == "Misc";

    let (child_to_parent, thread_mtimes) = scan_brain_threads(&brain_dir);

    let mut groups: HashMap<String, Vec<String>> = HashMap::new();
    for thread_id in thread_mtimes.keys() {
        let root_id = get_root_thread_id(thread_id, &child_to_parent);
        groups.entry(root_id).or_default().push(thread_id.clone());
    }

    let mut thread_logs = Vec::new();

    for (root_id, mut members) in groups {
        members.sort_by(|a, b| {
            thread_mtimes.get(a).cloned().unwrap_or(0)
                .cmp(&thread_mtimes.get(b).cloned().unwrap_or(0))
                .then_with(|| a.cmp(b))
        });
        
        let root_thread_id = &root_id;
        let latest_thread_id = members.last().unwrap();
        
        let root_dir = brain_dir.join(root_thread_id);
        let root_filepath = root_dir.join(".system_generated").join("logs").join("transcript.jsonl");

        let latest_dir = brain_dir.join(latest_thread_id);
        let latest_filepath = latest_dir.join(".system_generated").join("logs").join("transcript.jsonl");

        if !root_filepath.exists() || !latest_filepath.exists() {
            continue;
        }

        let info = match get_cached_thread_info(&latest_filepath, latest_thread_id) {
            Some(i) => i,
            None => continue,
        };

        let root_info = match get_cached_thread_info(&root_filepath, root_thread_id) {
            Some(i) => i,
            None => continue,
        };

        let matched = if is_misc {
            info.project_path.is_none()
        } else {
            if let Some(ref p_path) = info.project_path {
                if let Some(pos) = p_path.find(&project_path) {
                    let after_match = &p_path[pos + project_path.len()..];
                    let is_exact = match after_match.chars().next() {
                        Some(c) => !c.is_alphanumeric() && c != '_' && c != '-',
                        None => true,
                    };
                    is_exact
                } else {
                    false
                }
            } else {
                false
            }
        };

        if matched {
            let latest_mtime = thread_mtimes.get(latest_thread_id).cloned().unwrap_or(0);

            thread_logs.push(ThreadLog {
                id: root_id,
                latest_leaf_id: latest_thread_id.clone(),
                title: info.title,
                snippet: info.snippet,
                filepath: root_filepath.to_string_lossy().to_string(),
                mtime: latest_mtime,
                detected_project_path: Some(project_path.clone()),
            });
        }
    }

    thread_logs.sort_by(|a, b| b.mtime.cmp(&a.mtime).then_with(|| a.id.cmp(&b.id)));
    Ok(thread_logs)
}

fn detect_project_path(content: &str) -> Option<String> {
    let home = std::env::var("HOME").ok()?;
    let projects_prefix = format!("{}/projects/", home);
    
    // Normalize content to use current home instead of legacy user matthewmurphy
    let normalized_content = content.replace("/Users/matthewmurphy", &home);
    
    if let Some(pos) = normalized_content.find(&projects_prefix) {
        let after_prefix = &normalized_content[pos + projects_prefix.len()..];
        let end_pos = after_prefix.find(|c: char| {
            c == '/' || c == '"' || c == '\'' || c == '\\' || c == ',' || c == '`' || c == '*' || c == ')' || c == ']' || c == '}' || c == ':' || c == ';' || c == '.' || c.is_whitespace()
        }).unwrap_or(after_prefix.len());
        
        let mut project_name = &after_prefix[..end_pos];
        while !project_name.is_empty() && project_name.ends_with(|c: char| c == '`' || c == '*' || c == '.' || c == ',' || c == '`' || c == ':' || c == ';' || c == ')' || c == ']') {
            project_name = &project_name[..project_name.len() - 1];
        }
        if !project_name.is_empty() {
            return Some(format!("{}{}", projects_prefix, project_name));
        }
    }
    None
}

#[tauri::command]
fn get_all_agy_threads() -> Result<Vec<ThreadLog>, String> {
    use std::path::Path;

    let home = std::env::var("HOME").map_err(|_| "Could not find HOME directory".to_string())?;
    let brain_dir = Path::new(&home)
        .join(".gemini")
        .join("antigravity-cli")
        .join("brain");

    if !brain_dir.exists() {
        return Ok(Vec::new());
    }

    let (child_to_parent, thread_mtimes) = scan_brain_threads(&brain_dir);

    let mut groups: HashMap<String, Vec<String>> = HashMap::new();
    for thread_id in thread_mtimes.keys() {
        let root_id = get_root_thread_id(thread_id, &child_to_parent);
        groups.entry(root_id).or_default().push(thread_id.clone());
    }

    let mut thread_logs = Vec::new();

    for (root_id, mut members) in groups {
        members.sort_by(|a, b| {
            thread_mtimes.get(a).cloned().unwrap_or(0)
                .cmp(&thread_mtimes.get(b).cloned().unwrap_or(0))
                .then_with(|| a.cmp(b))
        });
        
        let root_thread_id = &root_id;
        let latest_thread_id = members.last().unwrap();
        
        let root_dir = brain_dir.join(root_thread_id);
        let root_filepath = root_dir.join(".system_generated").join("logs").join("transcript.jsonl");

        let latest_dir = brain_dir.join(latest_thread_id);
        let latest_filepath = latest_dir.join(".system_generated").join("logs").join("transcript.jsonl");

        if !root_filepath.exists() || !latest_filepath.exists() {
            continue;
        }

        let info = match get_cached_thread_info(&latest_filepath, latest_thread_id) {
            Some(i) => i,
            None => continue,
        };

        let root_info = match get_cached_thread_info(&root_filepath, root_thread_id) {
            Some(i) => i,
            None => continue,
        };

        let latest_mtime = thread_mtimes.get(latest_thread_id).cloned().unwrap_or(0);

        thread_logs.push(ThreadLog {
            id: root_id,
            latest_leaf_id: latest_thread_id.clone(),
            title: info.title,
            snippet: info.snippet,
            filepath: root_filepath.to_string_lossy().to_string(),
            mtime: latest_mtime,
            detected_project_path: info.project_path,
        });
    }

    thread_logs.sort_by(|a, b| b.mtime.cmp(&a.mtime).then_with(|| a.id.cmp(&b.id)));
    Ok(thread_logs)
}

#[tauri::command]
fn delete_thread(id: String) -> Result<(), String> {
    use std::path::Path;

    let home = std::env::var("HOME").map_err(|_| "Could not find HOME directory".to_string())?;
    let brain_dir = Path::new(&home)
        .join(".gemini")
        .join("antigravity-cli")
        .join("brain");

    if !brain_dir.exists() {
        return Ok(());
    }

    let (child_to_parent, thread_mtimes) = scan_brain_threads(&brain_dir);
    let root_id = get_root_thread_id(&id, &child_to_parent);

    for thread_id in thread_mtimes.keys() {
        if get_root_thread_id(thread_id, &child_to_parent) == root_id {
            let thread_dir = brain_dir.join(thread_id);
            if thread_dir.exists() {
                let _ = std::fs::remove_dir_all(&thread_dir);
            }
        }
    }
    
    // In case it wasn't in mtimes
    let root_dir = brain_dir.join(&root_id);
    if root_dir.exists() {
        let _ = std::fs::remove_dir_all(&root_dir);
    }

    Ok(())
}

#[tauri::command]
fn save_prompt_draft(project_path: String, content: String) -> Result<(), String> {
    use std::fs;
    use std::path::Path;

    let home = std::env::var("HOME").map_err(|_| "Could not find HOME directory".to_string())?;
    let drafts_dir = Path::new(&home)
        .join(".gemini")
        .join("antigravity-cli")
        .join("drafts");

    if !drafts_dir.exists() {
        fs::create_dir_all(&drafts_dir).map_err(|e| format!("Failed to create drafts directory: {}", e))?;
    }

    let safe_filename = project_path
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
        + ".txt";

    let draft_path = drafts_dir.join(safe_filename);
    fs::write(draft_path, content).map_err(|e| format!("Failed to write prompt draft: {}", e))?;
    Ok(())
}

#[tauri::command]
fn load_prompt_draft(project_path: String) -> Result<String, String> {
    use std::fs;
    use std::path::Path;

    let home = std::env::var("HOME").map_err(|_| "Could not find HOME directory".to_string())?;
    let drafts_dir = Path::new(&home)
        .join(".gemini")
        .join("antigravity-cli")
        .join("drafts");

    let safe_filename = project_path
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
        + ".txt";

    let draft_path = drafts_dir.join(safe_filename);
    if draft_path.exists() {
        fs::read_to_string(draft_path).map_err(|e| format!("Failed to read prompt draft: {}", e))
    } else {
        Ok(String::new())
    }
}

fn get_thread_id_from_path(filepath: &str) -> Option<String> {
    let path = std::path::Path::new(filepath);
    for ancestor in path.ancestors() {
        if let Some(parent) = ancestor.parent() {
            if parent.file_name()?.to_string_lossy() == "brain" {
                return Some(ancestor.file_name()?.to_string_lossy().to_string());
            }
        }
    }
    None
}

#[tauri::command]
fn read_thread_log(filepath: String) -> Result<String, String> {
    use std::fs;
    use std::path::Path;

    let home = std::env::var("HOME").map_err(|_| "Could not find HOME directory".to_string())?;
    let brain_dir = Path::new(&home)
        .join(".gemini")
        .join("antigravity-cli")
        .join("brain");

    if let Some(thread_id) = get_thread_id_from_path(&filepath) {
        if brain_dir.exists() {
            let (child_to_parent, thread_mtimes) = scan_brain_threads(&brain_dir);
            let root_id = get_root_thread_id(&thread_id, &child_to_parent);
            let chain = get_thread_chain(&root_id, &child_to_parent, &thread_mtimes);
            
            if !chain.is_empty() {
                let mut combined_content = String::new();
                for id in chain {
                    let log_path = brain_dir.join(id).join(".system_generated").join("logs").join("transcript.jsonl");
                    if log_path.exists() {
                        if let Ok(content) = fs::read_to_string(log_path) {
                            if !combined_content.is_empty() && !combined_content.ends_with('\n') {
                                combined_content.push('\n');
                            }
                            combined_content.push_str(&content);
                        }
                    }
                }
                return Ok(combined_content);
            }
        }
    }

    fs::read_to_string(filepath).map_err(|e| format!("Failed to read thread log: {}", e))
}

#[tauri::command]
fn file_exists(filepath: String) -> bool {
    std::path::Path::new(&filepath).exists()
}

#[tauri::command]
fn patch_thread_log_with_output(
    project_path: String,
    active_thread_id: Option<String>,
    output_content: String,
) -> Result<String, String> {
    use std::fs;
    use std::path::Path;
    use std::io::Read;

    let home = std::env::var("HOME").map_err(|_| "Could not find HOME directory".to_string())?;
    let brain_dir = Path::new(&home)
        .join(".gemini")
        .join("antigravity-cli")
        .join("brain");

    if !brain_dir.exists() {
        return Err("Brain directory does not exist".to_string());
    }

    // 1. Locate the correct thread directory ID
    let target_id = if let Some(ref id) = active_thread_id {
        if !id.trim().is_empty() {
            id.clone()
        } else {
            "".to_string()
        }
    } else {
        "".to_string()
    };

    let target_thread_id = if !target_id.is_empty() {
        let (child_to_parent, thread_mtimes) = scan_brain_threads(&brain_dir);
        let root_id = get_root_thread_id(&target_id, &child_to_parent);
        let mut chain = get_thread_chain(&root_id, &child_to_parent, &thread_mtimes);
        if let Some(leaf_id) = chain.pop() {
            leaf_id
        } else {
            target_id
        }
    } else {
        // Find the most recently modified thread that matches this project
        let entries = fs::read_dir(&brain_dir)
            .map_err(|e| format!("Failed to read brain directory: {}", e))?;

        let mut latest_thread_id = None;
        let mut latest_mtime = 0;

        for entry in entries {
            if let Ok(entry) = entry {
                let path = entry.path();
                if path.is_dir() {
                    let thread_id = path.file_name().unwrap().to_string_lossy().to_string();
                    let transcript_path = path.join(".system_generated").join("logs").join("transcript.jsonl");

                    if transcript_path.exists() {
                        if let Ok(metadata) = fs::metadata(&transcript_path) {
                            let mtime = metadata.modified()
                                .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e)))
                                .map(|d| d.as_secs())
                                .unwrap_or(0);

                            if mtime > latest_mtime {
                                if let Ok(file) = fs::File::open(&transcript_path) {
                                    let mut buffer = Vec::new();
                                    let _ = file.take(131072).read_to_end(&mut buffer);
                                    let content = String::from_utf8_lossy(&buffer);

                                    if let Some(pos) = content.find(&project_path) {
                                        let after_match = &content[pos + project_path.len()..];
                                        let is_exact = match after_match.chars().next() {
                                            Some(c) => !c.is_alphanumeric() && c != '_' && c != '-',
                                            None => true,
                                        };
                                        if is_exact {
                                            latest_mtime = mtime;
                                            latest_thread_id = Some(thread_id);
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        match latest_thread_id {
            Some(id) => id,
            None => return Err("No matching thread found for this project".to_string()),
        }
    };

    let thread_dir = brain_dir.join(&target_thread_id);
    let transcript_path = thread_dir.join(".system_generated").join("logs").join("transcript.jsonl");
    let transcript_full_path = thread_dir.join(".system_generated").join("logs").join("transcript_full.jsonl");

    let patch_file = |path: &Path| -> Result<(), String> {
        if !path.exists() {
            return Ok(());
        }
        let content = fs::read_to_string(path)
            .map_err(|e| format!("Failed to read transcript: {}", e))?;
        
        let mut lines: Vec<String> = content.lines().map(|s| s.to_string()).collect();
        let mut patched = false;

        // Iterate backwards to find the last planner response from the model
        for i in (0..lines.len()).rev() {
            if let Ok(mut obj) = serde_json::from_str::<serde_json::Value>(&lines[i]) {
                if obj.get("source").and_then(|v| v.as_str()) == Some("MODEL") 
                    && obj.get("type").and_then(|v| v.as_str()) == Some("PLANNER_RESPONSE")
                    && obj.get("content").is_some() 
                {
                    obj["content"] = serde_json::Value::String(output_content.clone());
                    if let Ok(new_line) = serde_json::to_string(&obj) {
                        lines[i] = new_line;
                        patched = true;
                        break;
                    }
                }
            }
        }

        if patched {
            let mut new_content = lines.join("\n");
            if !new_content.ends_with('\n') && !new_content.is_empty() {
                new_content.push('\n');
            }
            fs::write(path, new_content)
                .map_err(|e| format!("Failed to write patched transcript: {}", e))?;
        }
        Ok(())
    };

    patch_file(&transcript_path)?;
    patch_file(&transcript_full_path)?;

    Ok(target_thread_id)
}

#[tauri::command]
fn open_devtools(window: tauri::Window) {
    window.open_devtools();
}

#[tauri::command]
fn get_quota(state: tauri::State<AppState>) -> Result<String, String> {
    let mut cmd = std::process::Command::new("ag-quota");
    
    let home = std::env::var("HOME").unwrap_or_default();
    let log_dir_path = format!("{}/.gemini/antigravity-cli/log", home);
    
    let mut found_email = None;
    if let Ok(entries) = std::fs::read_dir(&log_dir_path) {
        let mut paths: Vec<_> = entries
            .filter_map(|e| e.ok())
            .map(|e| e.path())
            .filter(|p| p.is_file())
            .collect();
        paths.sort(); // Sorts chronologically since format is cli-YYYYMMDD_HHMMSS.log
        
        for path in paths.iter().rev() {
            if let Ok(content) = std::fs::read_to_string(path) {
                for line in content.lines().rev() {
                    if let Some(idx) = line.find("authenticated successfully as ") {
                        let email = line[idx + "authenticated successfully as ".len()..].trim();
                        if !email.is_empty() {
                            found_email = Some(email.to_string());
                            break;
                        }
                    }
                }
            }
            if found_email.is_some() {
                break;
            }
        }
        
        if let Some(ref email) = found_email {
            cmd.arg("--account").arg(email);
            
            // Check if active account changed to clear and duplicate tmux sessions from the new one
            let mut last_acct = state.last_active_account.lock().map_err(|e| e.to_string())?;
            if let Some(ref last) = *last_acct {
                if last != email {
                    println!("[DEBUG] Account changed from {} to {}. Clearing all project PTY sessions.", last, email);
                    
                    // Lock sessions and clear them
                    let mut sessions = state.sessions.lock().map_err(|e| e.to_string())?;
                    sessions.clear();
                    
                    // Kill all tmux sessions starting with "ai_os_"
                    if is_tmux_available() {
                        if let Ok(output) = std::process::Command::new("tmux")
                            .args(&["list-sessions", "-F", "#S"])
                            .output() {
                            let sessions_str = String::from_utf8_lossy(&output.stdout);
                            for line in sessions_str.lines() {
                                let session_name = line.trim();
                                if session_name.starts_with("ai_os_") {
                                    println!("[DEBUG] Killing tmux session on account change: {}", session_name);
                                    let _ = std::process::Command::new("tmux")
                                        .args(&["kill-session", "-t", session_name])
                                        .status();
                                }
                            }
                        }
                    }
                    
                    // Emit event to notify frontend that account has changed
                    let _ = state.app_handle.emit_all("account-changed", email.clone());
                }
            }
            *last_acct = Some(email.clone());
        }
    }

    let output = cmd
        .arg("-j")
        .output()
        .map_err(|e| e.to_string())?;
    Ok(String::from_utf8_lossy(&output.stdout).to_string())
}

#[derive(serde::Serialize, serde::Deserialize)]
pub struct BrowserContext {
    pub url: String,
    pub title: String,
    pub inner_text: String,
}

#[tauri::command]
async fn get_browser_context() -> Result<BrowserContext, String> {
    let script = r#"
        try {
            var chrome = Application('Google Chrome Canary');
            if (chrome.windows.length === 0) {
                JSON.stringify({error: "No windows open"});
            } else {
                var tab = chrome.windows[0].activeTab();
                var url = tab.url();
                var title = tab.title();
                
                var js = `
                    (function() {
                        var text = document.body ? document.body.innerText : "";
                        if (text.length > 20000) {
                            text = text.substring(0, 20000) + "... [truncated]";
                        }
                        return text;
                    })();
                `;
                
                var inner_text = tab.execute({javascript: js}) || "";
                
                JSON.stringify({
                    url: url || "",
                    title: title || "",
                    inner_text: inner_text
                });
            }
        } catch (e) {
            JSON.stringify({error: e.toString()});
        }
    "#;

    let output = std::process::Command::new("osascript")
        .arg("-l")
        .arg("JavaScript")
        .arg("-e")
        .arg(script)
        .output()
        .map_err(|e| format!("osascript failed to execute: {}", e))?;

    if !output.status.success() {
        let err_msg = String::from_utf8_lossy(&output.stderr).into_owned();
        return Err(format!("osascript error: {}", err_msg));
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    
    let data: serde_json::Value = serde_json::from_str(stdout.trim()).map_err(|e| format!("Failed to parse browser context JSON: {}", e))?;
    
    if let Some(err) = data.get("error") {
        let err_str = err.as_str().unwrap_or("Unknown error from browser script");
        if err_str.contains("Executing JavaScript through AppleScript is turned off") {
            return Err("JavaScript via Apple Events is disabled in Chrome Canary. Enable it via View > Developer > Allow JavaScript from Apple Events.".to_string());
        }
        return Err(err_str.to_string());
    }

    Ok(BrowserContext {
        url: data.get("url").and_then(|v| v.as_str()).unwrap_or("").to_string(),
        title: data.get("title").and_then(|v| v.as_str()).unwrap_or("").to_string(),
        inner_text: data.get("inner_text").and_then(|v| v.as_str()).unwrap_or("").to_string(),
    })
}

#[tauri::command]
fn dispatch_to_gemini(app_handle: tauri::AppHandle, prompt: String, context: Option<BrowserContext>) -> Result<(), String> {
    let mut final_prompt = prompt;
    if let Some(ctx) = context {
        final_prompt = format!("{}\n\n[Browser Context]\nURL: {}\nTitle: {}\n\n{}", final_prompt, ctx.url, ctx.title, ctx.inner_text);
    }
    
    let init_script = r#"
        window.__TAURI__.event.listen('populate-gemini-prompt', (event) => {
            const promptText = event.payload;
            
            const checkExist = setInterval(function() {
                const inputBox = document.querySelector('rich-textarea') || document.querySelector('div[contenteditable="true"]') || document.querySelector('textarea');
                if (inputBox) {
                    clearInterval(checkExist);
                    
                    if (inputBox.tagName.toLowerCase() === 'rich-textarea' || inputBox.hasAttribute('contenteditable')) {
                        inputBox.innerHTML = '';
                        inputBox.appendChild(document.createTextNode(promptText));
                    } else {
                        inputBox.value = promptText;
                    }
                    
                    inputBox.dispatchEvent(new Event('input', { bubbles: true }));
                    
                    setTimeout(() => {
                        const sendBtns = Array.from(document.querySelectorAll('button')).filter(b => 
                            (b.getAttribute('aria-label') || '').toLowerCase().includes('send') ||
                            (b.getAttribute('mattooltip') || '').toLowerCase().includes('send')
                        );
                        let sendBtn = sendBtns[0] || document.querySelector('button[type="submit"]');
                        if (sendBtn) {
                            sendBtn.click();
                        }
                    }, 500);
                }
            }, 500);
        });
    "#;

    if let Some(window) = app_handle.get_window("gemini_mode") {
        let _ = window.set_focus();
        window.emit("populate-gemini-prompt", final_prompt).map_err(|e| e.to_string())?;
    } else {
        let window = tauri::WindowBuilder::new(
            &app_handle,
            "gemini_mode",
            tauri::WindowUrl::External("https://gemini.google.com".parse().unwrap())
        )
        .title("Gemini")
        .initialization_script(init_script)
        .build()
        .map_err(|e| e.to_string())?;
        
        let final_prompt_clone = final_prompt.clone();
        std::thread::spawn(move || {
            std::thread::sleep(std::time::Duration::from_millis(3000));
            let _ = window.emit("populate-gemini-prompt", final_prompt_clone);
        });
    }
    
    Ok(())
}

#[tauri::command]
fn read_thread_notes_file() -> Result<String, String> {
    let home = std::env::var("HOME").map_err(|_| "Could not find HOME directory".to_string())?;
    let path = std::path::Path::new(&home).join("Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/thread-notes.md");
    std::fs::read_to_string(path).or_else(|_| Ok("".to_string()))
}

#[tauri::command]
fn write_thread_notes_file(content: String) -> Result<(), String> {
    let home = std::env::var("HOME").map_err(|_| "Could not find HOME directory".to_string())?;
    let path = std::path::Path::new(&home).join("Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/thread-notes.md");
    if let Some(parent) = path.parent() {
        let _ = std::fs::create_dir_all(parent);
    }
    std::fs::write(path, content).map_err(|e| e.to_string())
}

fn main() {
    let path = std::env::var("PATH").unwrap_or_else(|_| "/usr/bin:/bin:/usr/sbin:/sbin".to_string());
    let home = std::env::var("HOME").unwrap_or_default();
    let new_path = format!(
        "/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:{}/.local/bin:{}/.cargo/bin:{}/.gemini/antigravity-cli/bin:{}/.nvm/versions/node/v18.17.0/bin:{}/.nvm/versions/node/v26.3.0/bin:{}/bin:{}",
        home, home, home, home, home, home, path
    );
    std::env::set_var("PATH", new_path);

    let context = tauri::generate_context!();
    tauri::Builder::default()
        .menu(tauri::Menu::os_default(&context.package_info().name))
        .setup(|app| {
            let app_handle = app.handle();
    let floating_init_script = r#"
        (function() {
            function initIsolation() {
              const target = document.querySelector('.input-area-container');
              
              if (!target) {
                setTimeout(initIsolation, 500);
                return;
              }

              target.style.setProperty('z-index', '9999999', 'important');

              // 1. Traverse and hide structural siblings
              let current = target;
              while (current && current !== document.body && current !== document.documentElement) {
                const siblings = current.parentElement.children;
                
                for (let sibling of siblings) {
                  if (sibling !== current) {
                    sibling.style.visibility = 'hidden';
                    sibling.style.pointerEvents = 'none';
                  }
                }
                
                current.style.visibility = 'visible';
                if (current !== target) {
                  current.style.background = 'transparent';
                  current.style.backgroundImage = 'none'; 
                }
                
                current = current.parentElement;
              }

              // 2. Set the base background color to transparent
              document.documentElement.style.background = 'transparent';
              document.body.style.background = 'transparent';

              target.addEventListener('mousedown', (e) => {
                  if (e.target.tagName !== 'TEXTAREA' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'BUTTON' && !e.target.closest('button')) {
                      if (window.__TAURI__) {
                          window.__TAURI__.window.appWindow.startDragging();
                      }
                  }
              });

              // Robust auto-resizing
              let lastHeight = 324;
              let resizeTimeout;
              
              function calculateAndSetSize() {
                  let desiredHeight = 180; // Base height
                  
                  // 1. Generic way to find the main input area:
                  const textboxes = Array.from(document.querySelectorAll('textarea, [contenteditable=\"true\"], rich-textarea'));
                  let mainInput = null;
                  let maxArea = 0;
                  for (const tb of textboxes) {
                      const rect = tb.getBoundingClientRect();
                      const area = rect.width * rect.height;
                      if (area > maxArea) {
                          maxArea = area;
                          mainInput = tb;
                      }
                  }
                  
                  if (mainInput) {
                      const rect = mainInput.getBoundingClientRect();
                      // Assuming default height is ~50-60. If it grows, we add the difference.
                      if (rect.height > 60) {
                          desiredHeight += (rect.height - 60);
                      }
                  }
                  
                  // 2. Generic way to detect if there's a chat history:
                  let hasHistory = false;
                  // Fast path for Gemini
                  if (document.querySelector('user-message, model-message, message-list')) {
                      hasHistory = true;
                  } else {
                      // Generic fallback: check if body innerText length is significantly larger than input length
                      let inputText = mainInput ? (mainInput.value || mainInput.innerText || \"\") : \"\";
                      let bodyText = document.body.innerText || \"\";
                      if (bodyText.length - inputText.length > 500) {
                          hasHistory = true;
                      }
                  }
                  
                  if (hasHistory) {
                      desiredHeight = 800;
                  }
                  
                  desiredHeight = Math.round(desiredHeight * 1.8);
                  
                  // Clamp
                  desiredHeight = Math.max(324, Math.min(1440, desiredHeight));
                  
                  if (Math.abs(desiredHeight - lastHeight) > 5) {
                      lastHeight = desiredHeight;
                      if (window.__TAURI__) {
                          window.__TAURI__.window.appWindow.setSize(new window.__TAURI__.window.PhysicalSize(960, desiredHeight));
                      }
                  }
              }

              const resizeObserver = new ResizeObserver(() => {
                  clearTimeout(resizeTimeout);
                  resizeTimeout = setTimeout(calculateAndSetSize, 50);
              });
              resizeObserver.observe(document.body);
              
              const mutObserver = new MutationObserver(() => {
                  clearTimeout(resizeTimeout);
                  resizeTimeout = setTimeout(calculateAndSetSize, 50);
              });
              mutObserver.observe(document.body, { childList: true, subtree: true, characterData: true });
              // 3. Tactic A: Strip the classes responsible for triggering the ::before element
              const chatWindow = document.querySelector('chat-window');
              if (chatWindow) {
                chatWindow.classList.remove('show-lm-background', 'lm-canvas-styling');
              }

              // 4. Tactic B: Constructable Stylesheets (Bypasses <style> tag CSP restrictions)
              try {
                const sheet = new CSSStyleSheet();
                sheet.replaceSync(`
                  chat-window::before, 
                  chat-window::after {
                    display: none !important;
                    background-image: none !important;
                    opacity: 0 !important;
                  }
                  chat-app {
                    padding-top: 0px !important;
                  }
                  .input-area-container {
                    z-index: 9999999 !important;
                  }
                `);
                // Append the new stylesheet to the document's adopted stylesheets
                document.adoptedStyleSheets = [...document.adoptedStyleSheets, sheet];
              } catch (e) {
                console.log('Constructable stylesheets blocked or unsupported, relying on class removal.', e);
              }

              document.addEventListener('keydown', (e) => {
                  if (e.metaKey && e.altKey && e.code === 'KeyI') {
                      if (window.__TAURI__) {
                          window.__TAURI__.invoke('open_devtools');
                      }
                  }
              });

              //  5. Get rid of top padding (with dynamic observation)
              const applyChatAppPadding = () => {
                const chatApp = document.querySelector('chat-app');
                if (chatApp) {
                  chatApp.style.setProperty('padding-top', '0px', 'important');
                  chatApp.style.paddingTop = '0px';
                }
              };
              applyChatAppPadding();
              
              // Watch for changes to reapply padding if chat-app is dynamically loaded or re-rendered
              const chatAppObserver = new MutationObserver(applyChatAppPadding);
              chatAppObserver.observe(document.body, { childList: true, subtree: true });

            }
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initIsolation);
            } else {
                initIsolation();
            }
        })();
    "#;

    let floating_window = tauri::WindowBuilder::new(
        &app_handle,
        "floating",
        tauri::WindowUrl::External("https://gemini.google.com/app".parse().unwrap())
    )
    .title("Gemini Floating")
    .initialization_script(floating_init_script)
    .visible(false)
    .decorations(false)
    .transparent(true)
    .build()
    .unwrap();
    
    // Set initial size
    let _ = floating_window.set_size(tauri::Size::Physical(tauri::PhysicalSize { width: 960, height: 324 }));
            
            let app_handle_clone = app_handle.clone();
            let mut shortcut_manager = app.global_shortcut_manager();
            let _ = shortcut_manager.register("Cmd+Option+Space", move || {
                if let Some(window) = app_handle_clone.get_window("floating") {
                    if window.is_visible().unwrap_or(false) {
                        let _ = window.hide();
                    } else {
                        let _ = window.eval("window.location.href = 'https://gemini.google.com/app';");
                        let _ = window.show();
                        let _ = window.set_focus();
                    }
                }
            });

            spawn_axum_server(app_handle.clone());
            
            let sessions = Arc::new(Mutex::new(HashMap::new()));
            let active_project = Arc::new(Mutex::new(None));
            let staged_payload = Arc::new(Mutex::new(None));
            let last_active_account = Arc::new(Mutex::new(None));
            
            // Set up state
            app.manage(AppState {
                sessions,
                active_project,
                app_handle,
                staged_payload,
                last_active_account,
            });

            Ok(())
        })
        .on_page_load(|window, _| {
            let _ = window.eval(r#"
                document.addEventListener('keydown', (e) => {
                    if (e.metaKey && e.altKey && e.code === 'KeyI') {
                        if (window.__TAURI__) {
                            window.__TAURI__.invoke('open_devtools');
                        }
                    }
                });
            "#);
        })
        .invoke_handler(tauri::generate_handler![
            spawn_fresh_engine,
            initialize_project_session,
            prepare_spare_engine,
            switch_active_project,
            write_to_pty,
            resize_pty,
            is_engine_running,
            toggle_process_pause,
            close_project_session,
            select_directory,
            create_new_project,
            get_initial_project,
            get_project_threads,
            delete_thread,
            get_all_agy_threads,
            copy_tmux_selection,
            open_path,
            save_prompt_draft,
            load_prompt_draft,
            read_thread_log,
            file_exists,
            patch_thread_log_with_output,
            open_devtools,
            get_quota,
            get_browser_context,
            dispatch_to_gemini,
            search_project_threads,
            read_thread_notes_file,
            write_thread_notes_file,
            get_staged_payload,
            get_recent_workspaces,
            confirm_staged_execution
        ])
        .run(context)
        .expect("error while running tauri application");
}
#[derive(serde::Serialize, Clone)]
struct ThreadSearchResult {
    thread: ThreadLog,
    score: u64,
    preview: String,
}

#[tauri::command]
fn search_project_threads(project_path: String, query: String) -> Result<Vec<ThreadSearchResult>, String> {
    let threads = get_project_threads(project_path)?;
    let query_lower = query.to_lowercase();
    let mut results = Vec::new();
    
    let home = std::env::var("HOME").map_err(|_| "Could not find HOME".to_string())?;
    let brain_dir = std::path::Path::new(&home).join(".gemini").join("antigravity-cli").join("brain");

    for thread in threads {
        let mut score: u64 = 0;
        let mut preview = String::new();
        
        if thread.title.to_lowercase().contains(&query_lower) {
            score += 100_000_000;
        }
        
        let latest_filepath = brain_dir.join(&thread.latest_leaf_id).join(".system_generated").join("logs").join("transcript.jsonl");
        if let Ok(content) = std::fs::read_to_string(&latest_filepath) {
            for line in content.lines() {
                if let Ok(parsed) = serde_json::from_str::<serde_json::Value>(line) {
                    let step_type = parsed.get("type").and_then(|v| v.as_str()).unwrap_or("");
                    let content_str = parsed.get("content").and_then(|v| v.as_str()).unwrap_or("");
                    
                    if step_type == "USER_INPUT" {
                        let user_prompt = extract_user_request(content_str);
                        if user_prompt.to_lowercase().contains(&query_lower) {
                            score += 50_000_000;
                            if preview.is_empty() {
                                preview = truncate_preview(&user_prompt, &query_lower);
                            }
                        }
                    } else if step_type == "PLANNER_RESPONSE" || step_type == "MODEL" {
                        if content_str.to_lowercase().contains(&query_lower) {
                            score += 10_000_000;
                            if preview.is_empty() {
                                preview = truncate_preview(content_str, &query_lower);
                            }
                        }
                    }
                }
            }
        }
        
        if score > 0 {
            score += thread.mtime as u64;
            results.push(ThreadSearchResult {
                thread,
                score,
                preview: if preview.is_empty() { "Matched in title".to_string() } else { preview },
            });
        }
    }
    
    results.sort_by(|a, b| b.score.cmp(&a.score));
    Ok(results)
}

fn extract_user_request(content: &str) -> String {
    if let Some(start) = content.find("<USER_REQUEST>") {
        if let Some(end) = content.find("</USER_REQUEST>") {
            return content[start + 14..end].trim().to_string();
        }
    }
    content.to_string()
}

fn truncate_preview(content: &str, query: &str) -> String {
    let lower = content.to_lowercase();
    if let Some(pos) = lower.find(query) {
        let start = pos.saturating_sub(30);
        let end = (pos + query.len() + 80).min(content.len());
        let mut prev = String::new();
        if start > 0 { prev.push_str("..."); }
        prev.push_str(&content[start..end]);
        if end < content.len() { prev.push_str("..."); }
        prev.replace('\n', " ")
    } else {
        content.chars().take(100).collect::<String>().replace('\n', " ")
    }
}

#[derive(serde::Serialize, serde::Deserialize, Clone)]
struct WorkspaceItem {
    path: String,
    last_used: u64,
}

#[derive(serde::Serialize, serde::Deserialize, Clone)]
struct WorkspacesConfig {
    recent: Vec<WorkspaceItem>,
    pinned: Vec<WorkspaceItem>,
}

#[tauri::command]
fn get_staged_payload(state: tauri::State<AppState>) -> Result<Option<ExecutionPayload>, String> {
    let staged = state.staged_payload.lock().map_err(|e| e.to_string())?;
    Ok(staged.clone())
}

#[tauri::command]
fn get_recent_workspaces() -> Result<WorkspacesConfig, String> {
    let home = std::env::var("HOME").map_err(|e| e.to_string())?;
    let path = std::path::Path::new(&home)
        .join(".gemini")
        .join("antigravity-cli")
        .join("workspaces.json");
    if path.exists() {
        let content = std::fs::read_to_string(&path).map_err(|e| e.to_string())?;
        let config: WorkspacesConfig = serde_json::from_str(&content).map_err(|e| e.to_string())?;
        Ok(config)
    } else {
        Ok(WorkspacesConfig {
            recent: vec![],
            pinned: vec![],
        })
    }
}

#[tauri::command]
fn confirm_staged_execution(
    project_path: String,
    engine: String,
    mode: String,
    payload: String,
    state: tauri::State<AppState>,
) -> Result<(), String> {
    let agent_logs_dir = std::path::Path::new(&project_path).join(".agent-logs");
    std::fs::create_dir_all(&agent_logs_dir).map_err(|e| e.to_string())?;
    let payload_path = agent_logs_dir.join("current_task_payload.md");
    std::fs::write(&payload_path, &payload).map_err(|e| e.to_string())?;

    if let Ok(home) = std::env::var("HOME") {
        let workspaces_dir = std::path::Path::new(&home)
            .join(".gemini")
            .join("antigravity-cli");
        let _ = std::fs::create_dir_all(&workspaces_dir);
        let path = workspaces_dir.join("workspaces.json");
        let mut config = if path.exists() {
            let content = std::fs::read_to_string(&path).unwrap_or_default();
            serde_json::from_str::<WorkspacesConfig>(&content).unwrap_or(WorkspacesConfig {
                recent: vec![],
                pinned: vec![],
            })
        } else {
            WorkspacesConfig {
                recent: vec![],
                pinned: vec![],
            }
        };

        config.recent.retain(|w| w.path != project_path);
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        config.recent.insert(0, WorkspaceItem {
            path: project_path.clone(),
            last_used: now,
        });
        if config.recent.len() > 10 {
            config.recent.truncate(10);
        }
        if let Ok(serialized) = serde_json::to_string_pretty(&config) {
            let _ = std::fs::write(&path, serialized);
        }
    }

    let thread_id = {
        let staged = state.staged_payload.lock().map_err(|e| e.to_string())?;
        staged.as_ref().map(|s| s.thread_id.clone())
    };

    let switch_res = switch_active_project(project_path.clone(), engine.clone(), thread_id.clone(), state.clone())?;

    let prompt_text = format!(
        "Please read the instructions inside `.agent-logs/current_task_payload.md` and complete the task in {} mode.\n",
        if mode == "triage" { "Triage" } else { "Worker Bee" }
    );
    
    let app_handle = state.app_handle.clone();
    let project_path_clone = project_path.clone();
    let engine_clone = engine.clone();
    let thread_id_clone = thread_id.clone();
    std::thread::spawn(move || {
        std::thread::sleep(std::time::Duration::from_millis(if switch_res.is_new_session { 3000 } else { 1000 }));
        let state_inside = app_handle.state::<AppState>();
        let _ = write_to_pty(prompt_text, project_path_clone, engine_clone, thread_id_clone, state_inside);
    });

    if let Some(win) = state.app_handle.get_window("staging-overlay") {
        let _ = win.hide();
    }

    Ok(())
}
