use portable_pty::{CommandBuilder, MasterPty, NativePtySystem, PtySize, PtySystem};
use std::io::{Read, Write};
use std::sync::{Arc, Mutex};
use std::collections::HashMap;
use tauri::Manager;

// Project session containing its own PTY channels and shell process details
struct ProjectSession {
    pty_writer: Box<dyn Write + Send>,
    pty_master: Box<dyn MasterPty + Send>,
    shell_pid: u32,
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
}

fn is_tmux_available() -> bool {
    std::process::Command::new("which")
        .arg("tmux")
        .output()
        .map(|o| o.status.success())
        .unwrap_or(false)
}

fn has_tmux_session(session_name: &str) -> bool {
    std::process::Command::new("tmux")
        .args(&["has-session", "-t", session_name])
        .status()
        .map(|s| s.success())
        .unwrap_or(false)
}

fn get_tmux_session_name(project_path: &str) -> String {
    let sanitized: String = project_path
        .chars()
        .map(|c| if c.is_alphanumeric() { c } else { '_' })
        .collect();
    format!("ai_os_{}", sanitized.trim_matches('_'))
}

// Spawns a new shell PTY for a specific project directory
fn spawn_project_pty(
    project_path: &str,
    app_handle: &tauri::AppHandle,
    sessions_ref: Arc<Mutex<HashMap<String, ProjectSession>>>,
) -> Result<(u32, bool), String> {
    let pty_system = NativePtySystem::default();
    let pair = pty_system.openpty(PtySize {
        rows: 24,
        cols: 80,
        pixel_width: 0,
        pixel_height: 0,
    }).map_err(|e| e.to_string())?;

    let mut is_new_tmux = false;
    let cmd = if is_tmux_available() {
        let session_name = get_tmux_session_name(project_path);
        if !has_tmux_session(&session_name) {
            is_new_tmux = true;
        }
        let mut c = CommandBuilder::new("tmux");
        c.args(&["new-session", "-A", "-s", &session_name, "-c", project_path]);
        c
    } else {
        is_new_tmux = true;
        let mut c = CommandBuilder::new("/bin/zsh");
        c.cwd(project_path);
        c
    };

    let _child = pair.slave.spawn_command(cmd).map_err(|e| e.to_string())?;
    let shell_pid = _child.process_id().unwrap_or(0);

    let reader = pair.master.try_clone_reader().map_err(|e| e.to_string())?;
    let writer = pair.master.take_writer().map_err(|e| e.to_string())?;

    // Store in sessions map
    {
        let mut sessions = sessions_ref.lock().map_err(|e| e.to_string())?;
        sessions.insert(
            project_path.to_string(),
            ProjectSession {
                pty_writer: writer,
                pty_master: pair.master,
                shell_pid,
                project_path: project_path.to_string(),
            },
        );
    }

    // Spawn reader thread for this specific project PTY
    let app_handle_clone = app_handle.clone();
    let path_clone = project_path.to_string();
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
                    }).ok();
                }
                _ => break,
            }
        }
    });

    Ok((shell_pid, is_new_tmux))
}

#[derive(Clone, serde::Serialize)]
struct SwitchResult {
    shell_pid: u32,
    is_new_session: bool,
}

#[tauri::command]
fn initialize_project_session(project_path: String, state: tauri::State<AppState>) -> Result<u32, String> {
    let sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    if let Some(session) = sessions.get(&project_path) {
        return Ok(session.shell_pid);
    }
    drop(sessions); // release lock before spawning to avoid deadlock

    let (pid, _) = spawn_project_pty(&project_path, &state.app_handle, state.sessions.clone())?;
    Ok(pid)
}

#[tauri::command]
fn switch_active_project(project_path: String, state: tauri::State<AppState>) -> Result<SwitchResult, String> {
    let mut is_new_session = false;
    let mut shell_pid = 0;

    // First, ensure the session exists. If not, create it.
    let exists = {
        let sessions = state.sessions.lock().map_err(|e| e.to_string())?;
        if let Some(session) = sessions.get(&project_path) {
            shell_pid = session.shell_pid;
            true
        } else {
            false
        }
    };

    if !exists {
        let (pid, is_new) = spawn_project_pty(&project_path, &state.app_handle, state.sessions.clone())?;
        shell_pid = pid;
        is_new_session = is_new;
    }

    let mut active = state.active_project.lock().map_err(|e| e.to_string())?;
    *active = Some(project_path);
    Ok(SwitchResult {
        shell_pid,
        is_new_session,
    })
}

#[tauri::command]
fn write_to_pty(data: String, project_path: String, state: tauri::State<AppState>) -> Result<(), String> {
    let mut sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    if let Some(session) = sessions.get_mut(&project_path) {
        session.pty_writer.write_all(data.as_bytes()).map_err(|e| e.to_string())?;
        session.pty_writer.flush().map_err(|e| e.to_string())?;
        Ok(())
    } else {
        Err(format!("No PTY session found for project: {}", project_path))
    }
}

#[tauri::command]
fn resize_pty(rows: u16, cols: u16, project_path: String, state: tauri::State<AppState>) -> Result<(), String> {
    let sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    if let Some(session) = sessions.get(&project_path) {
        session.pty_master.resize(PtySize {
            rows,
            cols,
            pixel_width: 0,
            pixel_height: 0,
        }).map_err(|e| e.to_string())?;
        Ok(())
    } else {
        Err(format!("No PTY session found for project: {}", project_path))
    }
}

#[tauri::command]
fn is_engine_running(engine: String, project_path: String, state: tauri::State<AppState>) -> Result<bool, String> {
    let sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    let shell_pid = match sessions.get(&project_path) {
        Some(s) => s.shell_pid,
        None => return Ok(false),
    };
    drop(sessions);

    let output = std::process::Command::new("ps")
        .args(&["-A", "-o", "ppid,pid,args"])
        .output()
        .map_err(|e| e.to_string())?;
        
    let stdout = String::from_utf8_lossy(&output.stdout);
    
    use std::collections::HashMap as StdHashMap;
    let mut parent_to_children: StdHashMap<u32, Vec<(u32, String)>> = StdHashMap::new();
    
    for line in stdout.lines().skip(1) {
        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.len() >= 3 {
            if let (Ok(ppid), Ok(pid)) = (parts[0].parse::<u32>(), parts[1].parse::<u32>()) {
                let args = parts[2..].join(" ");
                parent_to_children.entry(ppid).or_default().push((pid, args));
            }
        }
    }
    
    let mut queue = vec![shell_pid];
    let mut visited = std::collections::HashSet::new();
    let target = engine.to_lowercase();
    
    while let Some(current_pid) = queue.pop() {
        if !visited.insert(current_pid) {
            continue;
        }
        if let Some(children) = parent_to_children.get(&current_pid) {
            for &(child_pid, ref args) in children {
                let args_lower = args.to_lowercase();
                if args_lower.contains(&target) {
                    return Ok(true);
                }
                queue.push(child_pid);
            }
        }
    }
    
    Ok(false)
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
fn toggle_process_pause(project_path: String, pause: bool, state: tauri::State<AppState>) -> Result<(), String> {
    let sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    let session = sessions.get(&project_path)
        .ok_or_else(|| format!("No active session for path: {}", project_path))?;
    let shell_pid = session.shell_pid;
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
            toggle_process_pause
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}