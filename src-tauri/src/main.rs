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
}

struct AppState {
    // Maps project path (canonical absolute path) to its session state
    sessions: Arc<Mutex<HashMap<String, ProjectSession>>>,
    // Tracks currently active project path
    active_project: Arc<Mutex<Option<String>>>,
    // Keep a clone of the app handle to emit events
    app_handle: tauri::AppHandle,
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

fn spawn_axum_server(app_handle: tauri::AppHandle) {
    tauri::async_runtime::spawn(async move {
        let cors = CorsLayer::new()
            .allow_origin(Any)
            .allow_methods(Any)
            .allow_headers(Any);

        let app = Router::new()
            .route("/api/context/sync", post(handle_sync))
            .route("/api/revision/commit", post(handle_commit))
            .route("/api/gemini/sync", post(handle_gemini_sync))
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

fn get_tmux_session_name(project_path: &str, terminal_type: &str) -> String {
    let sanitized: String = project_path
        .chars()
        .map(|c| if c.is_alphanumeric() { c } else { '_' })
        .collect();
    format!("ai_os_{}_{}", terminal_type, sanitized.trim_matches('_'))
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

fn is_engine_running_proc(engine: &str, project_path: &str, shell_pid: Option<u32>) -> bool {
    let root_pid = if is_tmux_available() {
        let session_name = get_tmux_session_name(project_path, engine);
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
        let session_name = get_tmux_session_name(project_path, terminal_type);
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
    if engine == "claude" {
        let mut agy_alive = false;
        let mut client_alive = false;
        if let Some(pid) = session.claude_pid {
            agy_alive = is_engine_running_proc("claude", project_path, session.claude_pid);
            client_alive = is_process_alive(pid);
        }
        if !agy_alive || !client_alive {
            if is_tmux_available() && !agy_alive {
                let session_name = get_tmux_session_name(project_path, "claude");
                if has_tmux_session(&session_name) {
                    let _ = std::process::Command::new("tmux")
                        .args(&["kill-session", "-t", &session_name])
                        .status();
                }
            }
            let (writer, master, pid, is_new) = spawn_single_pty(project_path, "claude", app_handle)?;
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
            agy_alive = is_engine_running_proc("agy", project_path, session.agy_pid);
            client_alive = is_process_alive(pid);
        }
        if !agy_alive || !client_alive {
            if is_tmux_available() && !agy_alive {
                let session_name = get_tmux_session_name(project_path, "agy");
                if has_tmux_session(&session_name) {
                    let _ = std::process::Command::new("tmux")
                        .args(&["kill-session", "-t", &session_name])
                        .status();
                }
            }
            let (writer, master, pid, is_new) = spawn_single_pty(project_path, "agy", app_handle)?;
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
        let (writer, master, pid, _) = spawn_single_pty(project_path, "mini", app_handle)?;
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
fn spawn_fresh_engine(project_path: String, engine: String, state: tauri::State<AppState>) -> Result<u32, String> {
    let app_handle = state.app_handle.clone();
    let mut sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    let session = sessions.get_mut(&project_path).ok_or_else(|| "No session found".to_string())?;

    if is_tmux_available() {
        let session_name = get_tmux_session_name(&project_path, &engine);
        if has_tmux_session(&session_name) {
            let _ = std::process::Command::new("tmux")
                .args(&["kill-session", "-t", &session_name])
                .status();
        }
    }

    let (writer, master, pid, _) = spawn_single_pty(&project_path, &engine, &app_handle)?;
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
    Ok(pid)
}

#[tauri::command]
fn initialize_project_session(project_path: String, state: tauri::State<AppState>) -> Result<u32, String> {
    let app_handle = state.app_handle.clone();
    let mut sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    if !sessions.contains_key(&project_path) {
        let (mini_writer, mini_master, mini_pid, _) = spawn_single_pty(&project_path, "mini", &app_handle)?;
        sessions.insert(
            project_path.clone(),
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
            },
        );
    }
    let session = sessions.get_mut(&project_path).unwrap();
    let (pid, _) = ensure_engine_pty(&project_path, "agy", &app_handle, session)?;
    Ok(pid)
}

#[tauri::command]
fn switch_active_project(project_path: String, engine: String, state: tauri::State<AppState>) -> Result<SwitchResult, String> {
    let app_handle = state.app_handle.clone();

    let mut sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    let is_new_proj = !sessions.contains_key(&project_path);
    if is_new_proj {
        // Spawn mini and engine PTYs in parallel to speed up tab loading
        let app_handle_clone1 = app_handle.clone();
        let app_handle_clone2 = app_handle.clone();
        let path_clone1 = project_path.clone();
        let path_clone2 = project_path.clone();
        let engine_clone = engine.clone();

        let mini_thread = std::thread::spawn(move || {
            spawn_single_pty(&path_clone1, "mini", &app_handle_clone1)
        });
        let engine_thread = std::thread::spawn(move || {
            spawn_single_pty(&path_clone2, &engine_clone, &app_handle_clone2)
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

        sessions.insert(project_path.clone(), session);

        let mut active = state.active_project.lock().map_err(|e| e.to_string())?;
        *active = Some(project_path.clone());

        trigger_tmux_refresh(&project_path, &engine);

        return Ok(SwitchResult {
            shell_pid: engine_pid,
            is_new_session,
        });
    }

    let session = sessions.get_mut(&project_path).unwrap();
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
fn write_to_pty(data: String, project_path: String, terminal_type: String, state: tauri::State<AppState>) -> Result<(), String> {
    let mut sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    if let Some(session) = sessions.get_mut(&project_path) {
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
fn resize_pty(rows: u16, cols: u16, project_path: String, terminal_type: String, state: tauri::State<AppState>) -> Result<(), String> {
    let sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    if let Some(session) = sessions.get(&project_path) {
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
fn is_engine_running(engine: String, project_path: String, state: tauri::State<AppState>) -> Result<bool, String> {
    let sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    let shell_pid = match sessions.get(&project_path) {
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

    Ok(is_engine_running_proc(&engine, &project_path, shell_pid))
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
fn toggle_process_pause(project_path: String, engine: String, pause: bool, state: tauri::State<AppState>) -> Result<(), String> {
    let sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    let session = sessions.get(&project_path)
        .ok_or_else(|| format!("No active session for path: {}", project_path))?;
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
    if let Some(_) = sessions.remove(&project_path) {
        for term_type in &["claude", "agy", "mini"] {
            let session_name = get_tmux_session_name(&project_path, term_type);
            let _ = std::process::Command::new("tmux")
                .args(&["-u", "kill-session", "-t", &session_name])
                .status();
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
fn copy_tmux_selection(project_path: String, terminal_type: String) -> Result<(), String> {
    if is_tmux_available() {
        let session_name = get_tmux_session_name(&project_path, &terminal_type);
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

#[derive(serde::Serialize)]
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

    for line in content.lines() {
        if let Ok(obj) = serde_json::from_str::<serde_json::Value>(line) {
            if obj.get("type").and_then(|v| v.as_str()) == Some("USER_INPUT") {
                if let Some(prompt_content) = obj.get("content").and_then(|v| v.as_str()) {
                    let mut raw_prompt = prompt_content.to_string();
                    if let Some(start_idx) = raw_prompt.find("<USER_REQUEST>") {
                        if let Some(end_idx) = raw_prompt.find("</USER_REQUEST>") {
                            raw_prompt = raw_prompt[start_idx + 14..end_idx].trim().to_string();
                        }
                    }
                    
                    let clean_prompt = raw_prompt.replace("\r", "").replace("\n", " ");
                    let char_count = clean_prompt.chars().count();
                    title = if char_count > 40 {
                        format!("{}...", clean_prompt.chars().take(40).collect::<String>())
                    } else {
                        clean_prompt.clone()
                    };
                    snippet = if char_count > 120 {
                        format!("{}...", clean_prompt.chars().take(120).collect::<String>())
                    } else {
                        clean_prompt
                    };
                    break;
                }
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
    
    if let Some(pos) = content.find(&projects_prefix) {
        let after_prefix = &content[pos + projects_prefix.len()..];
        let end_pos = after_prefix.find(|c: char| {
            c == '/' || c == '"' || c == '\'' || c == '\\' || c == ',' || c == '`' || c == '*' || c == ')' || c == ']' || c == '}' || c == ':' || c == ';' || c == '.' || c.is_whitespace()
        }).unwrap_or(after_prefix.len());
        
        let mut project_name = &after_prefix[..end_pos];
        while !project_name.is_empty() && project_name.ends_with(|c: char| c == '`' || c == '*' || c == '.' || c == ',' || c == ':' || c == ';' || c == ')' || c == ']') {
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
fn get_quota() -> Result<String, String> {
    let mut cmd = std::process::Command::new("ag-quota");
    
    let home = std::env::var("HOME").unwrap_or_default();
    let log_dir_path = format!("{}/.gemini/antigravity-cli/log", home);
    
    if let Ok(entries) = std::fs::read_dir(log_dir_path) {
        let mut paths: Vec<_> = entries
            .filter_map(|e| e.ok())
            .map(|e| e.path())
            .filter(|p| p.is_file())
            .collect();
        paths.sort(); // Sorts chronologically since format is cli-YYYYMMDD_HHMMSS.log
        
        let mut found_email = None;
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
        
        if let Some(email) = found_email {
            cmd.arg("--account").arg(email);
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

              // 2. Set the base background color
              const isDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
              const bgColor = isDarkMode ? '#131314' : '#ffffff';
              document.documentElement.style.background = bgColor;
              document.body.style.background = bgColor;

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
        tauri::WindowUrl::External("https://gemini.google.com".parse().unwrap())
    )
    .title("Gemini Floating")
    .initialization_script(floating_init_script)
    .visible(false)
    .build()
    .unwrap();
    
    // Set initial size
    let _ = floating_window.set_size(tauri::Size::Physical(tauri::PhysicalSize { width: 660, height: 80 }));
            
            let app_handle_clone = app_handle.clone();
            let mut shortcut_manager = app.global_shortcut_manager();
            let _ = shortcut_manager.register("Cmd+Option+Space", move || {
                if let Some(window) = app_handle_clone.get_window("floating") {
                    if window.is_visible().unwrap_or(false) {
                        let _ = window.hide();
                    } else {
                        let _ = window.show();
                        let _ = window.set_focus();
                    }
                }
            });

            spawn_axum_server(app_handle.clone());
            
            let sessions = Arc::new(Mutex::new(HashMap::new()));
            let active_project = Arc::new(Mutex::new(None));
            
            // Set up state
            app.manage(AppState {
                sessions,
                active_project,
                app_handle,
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
            dispatch_to_gemini
        ])
        .run(context)
        .expect("error while running tauri application");
}