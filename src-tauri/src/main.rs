use portable_pty::{CommandBuilder, MasterPty, NativePtySystem, PtySize, PtySystem};
use std::io::{Read, Write};
use std::sync::{Arc, Mutex};
use std::collections::HashMap;
use tauri::Manager;

// Project session containing its own PTY channels and shell process details
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
        .args(&["has-session", "-t", session_name])
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

fn is_pid_alive(pid: u32) -> bool {
    std::process::Command::new("kill")
        .args(&["-0", &pid.to_string()])
        .status()
        .map(|s| s.success())
        .unwrap_or(false)
}

fn is_session_alive(project_path: &str, engine: &str, pid: Option<u32>) -> bool {
    if is_tmux_available() {
        let session_name = get_tmux_session_name(project_path, engine);
        has_tmux_session(&session_name)
    } else {
        match pid {
            Some(p) => is_pid_alive(p),
            None => false,
        }
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
    let cmd = if is_tmux_available() {
        let session_name = get_tmux_session_name(project_path, terminal_type);
        if !has_tmux_session(&session_name) {
            is_new_tmux = true;
        }
        let mut c = CommandBuilder::new("tmux");
        let mut args = vec!["new-session".to_string(), "-A".to_string(), "-s".to_string(), session_name.clone(), "-c".to_string(), project_path.to_string()];
        if terminal_type == "claude" {
            args.push("claude --dangerously-skip-permissions".to_string());
        } else if terminal_type == "agy" {
            args.push(format!("agy --add-dir={} --dangerously-skip-permissions", project_path));
        }
        c.args(&args);

        if is_new_tmux {
            let session_name_clone = session_name.clone();
            std::thread::spawn(move || {
                std::thread::sleep(std::time::Duration::from_millis(150));
                let _ = std::process::Command::new("tmux")
                    .args(&["set-option", "-t", &session_name_clone, "status", "off"])
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

    let _child = pair.slave.spawn_command(cmd).map_err(|e| e.to_string())?;
    let shell_pid = _child.process_id().unwrap_or(0);

    let reader = pair.master.try_clone_reader().map_err(|e| e.to_string())?;
    let writer = pair.master.take_writer().map_err(|e| e.to_string())?;

    // Spawn reader thread for this specific PTY
    let app_handle_clone = app_handle.clone();
    let path_clone = project_path.to_string();
    let type_clone = terminal_type.to_string();
    std::thread::spawn(move || {
        let mut reader = reader;
        let mut buf = [0u8; 1024];
        loop {
            match reader.read(&mut buf) {
                Ok(n) if n > 0 => {
                    let data = String::from_utf8_lossy(&buf[..n]).to_string();
                    app_handle_clone.emit_all("pty-output", Payload {
                        data,
                        project_path: path_clone.clone(),
                        terminal_type: type_clone.clone(),
                    }).ok();
                }
                _ => break,
            }
        }
    });

    Ok((writer, pair.master, shell_pid, is_new_tmux))
}

fn ensure_engine_pty(
    project_path: &str,
    engine: &str,
    app_handle: &tauri::AppHandle,
    session: &mut ProjectSession,
) -> Result<(u32, bool), String> {
    if engine == "claude" {
        let is_alive = if session.claude_pid.is_some() {
            is_session_alive(project_path, "claude", session.claude_pid)
        } else {
            false
        };
        if !is_alive {
            let (writer, master, pid, is_new) = spawn_single_pty(project_path, "claude", app_handle)?;
            session.claude_writer = Some(writer);
            session.claude_master = Some(master);
            session.claude_pid = Some(pid);
            Ok((pid, is_new))
        } else {
            Ok((session.claude_pid.unwrap(), false))
        }
    } else if engine == "agy" {
        let is_alive = if session.agy_pid.is_some() {
            is_session_alive(project_path, "agy", session.agy_pid)
        } else {
            false
        };
        if !is_alive {
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

#[derive(Clone, serde::Serialize)]
struct SwitchResult {
    shell_pid: u32,
    is_new_session: bool,
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
        *active = Some(project_path);

        return Ok(SwitchResult {
            shell_pid: engine_pid,
            is_new_session,
        });
    }

    let session = sessions.get_mut(&project_path).unwrap();
    let (shell_pid, is_new_session) = ensure_engine_pty(&project_path, &engine, &app_handle, session)?;

    let mut active = state.active_project.lock().map_err(|e| e.to_string())?;
    *active = Some(project_path);
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

    Ok(is_session_alive(&project_path, &engine, shell_pid))
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
                .args(&["kill-session", "-t", &session_name])
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
fn get_initial_project() -> Option<String> {
    std::env::var("AIOS_INITIAL_PROJECT").ok()
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            let app_handle = app.handle();
            
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
        .invoke_handler(tauri::generate_handler![
            initialize_project_session,
            switch_active_project,
            write_to_pty,
            resize_pty,
            is_engine_running,
            toggle_process_pause,
            close_project_session,
            select_directory,
            create_new_project,
            get_initial_project
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}