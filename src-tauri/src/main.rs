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

// Spawns a new shell PTY for a specific project directory
fn spawn_project_pty(
    project_path: &str,
    app_handle: &tauri::AppHandle,
    sessions_ref: Arc<Mutex<HashMap<String, ProjectSession>>>,
) -> Result<u32, String> {
    let pty_system = NativePtySystem::default();
    let pair = pty_system.openpty(PtySize {
        rows: 24,
        cols: 80,
        pixel_width: 0,
        pixel_height: 0,
    }).map_err(|e| e.to_string())?;

    let mut cmd = CommandBuilder::new("/bin/zsh");
    // Start shell inside the target project directory!
    cmd.cwd(project_path);
    
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

    Ok(shell_pid)
}

#[tauri::command]
fn initialize_project_session(project_path: String, state: tauri::State<AppState>) -> Result<u32, String> {
    let sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    if let Some(session) = sessions.get(&project_path) {
        return Ok(session.shell_pid);
    }
    drop(sessions); // release lock before spawning to avoid deadlock

    spawn_project_pty(&project_path, &state.app_handle, state.sessions.clone())
}

#[tauri::command]
fn switch_active_project(project_path: String, state: tauri::State<AppState>) -> Result<(), String> {
    // First, ensure the session exists. If not, create it.
    let exists = {
        let sessions = state.sessions.lock().map_err(|e| e.to_string())?;
        sessions.contains_key(&project_path)
    };

    if !exists {
        spawn_project_pty(&project_path, &state.app_handle, state.sessions.clone())?;
    }

    let mut active = state.active_project.lock().map_err(|e| e.to_string())?;
    *active = Some(project_path);
    Ok(())
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
            is_engine_running
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}