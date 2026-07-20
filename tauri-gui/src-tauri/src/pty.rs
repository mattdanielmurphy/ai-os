use portable_pty::{CommandBuilder, MasterPty, NativePtySystem, PtySize, PtySystem};
use std::io::{Read, Write};
use std::collections::HashMap;
use tauri::Manager;

use crate::types::{AppState, Payload, ProjectSession};

// ---------------------------------------------------------------------------
// tmux helpers
// ---------------------------------------------------------------------------

pub fn is_tmux_available() -> bool {
    static AVAILABLE: std::sync::OnceLock<bool> = std::sync::OnceLock::new();
    *AVAILABLE.get_or_init(|| {
        std::process::Command::new("tmux")
            .arg("-V")
            .output()
            .map(|o| o.status.success())
            .unwrap_or(false)
    })
}

pub fn has_tmux_session(session_name: &str) -> bool {
    std::process::Command::new("tmux")
        .args(&["-u", "has-session", "-t", session_name])
        .status()
        .map(|s| s.success())
        .unwrap_or(false)
}

pub fn get_tmux_session_name(project_path: &str, terminal_type: &str, thread_id: Option<&str>) -> String {
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

pub fn get_tmux_pane_pid(session_name: &str) -> Option<u32> {
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

// ---------------------------------------------------------------------------
// process detection helpers
// ---------------------------------------------------------------------------

pub fn is_engine_running_proc(engine: &str, project_path: &str, thread_id: Option<&str>, shell_pid: Option<u32>) -> bool {
    if engine == "hermes" {
        return std::net::TcpStream::connect("127.0.0.1:9119").is_ok();
    }

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

    let mut parent_to_children: HashMap<u32, Vec<u32>> = HashMap::new();
    let mut pid_to_args: HashMap<u32, String> = HashMap::new();

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
            if engine == "claude" && args_lower.contains("claude") {
                return true;
            } else if engine == "agy" && args_lower.contains("agy") {
                return true;
            } else if engine == "hermes" && args_lower.contains("hermes") {
                return true;
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

pub fn trigger_tmux_refresh(_project_path: &str, _engine: &str) {
    if is_tmux_available() {
        std::thread::spawn(move || {
            std::thread::sleep(std::time::Duration::from_millis(200));
            let _ = std::process::Command::new("tmux")
                .args(&["-u", "refresh-client"])
                .status();
        });
    }
}

pub fn is_process_alive(pid: u32) -> bool {
    std::process::Command::new("kill")
        .args(&["-0", &pid.to_string()])
        .status()
        .map(|s| s.success())
        .unwrap_or(false)
}

// ---------------------------------------------------------------------------
// PTY spawning
// ---------------------------------------------------------------------------

pub fn spawn_single_pty(
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
        } else if terminal_type == "hermes" {
            args.push("hermes".to_string());
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
        } else if terminal_type == "hermes" {
            let mut c = CommandBuilder::new("hermes");
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
    if let Some(tid) = thread_id {
        cmd.env("AIOS_THREAD_ID", tid);
    }

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

// ---------------------------------------------------------------------------
// Hermes serve daemon
// ---------------------------------------------------------------------------

static HERMES_INIT: std::sync::atomic::AtomicBool = std::sync::atomic::AtomicBool::new(false);

pub fn ensure_hermes_serve_running() {
    let initialized = HERMES_INIT.load(std::sync::atomic::Ordering::Relaxed);
    let is_running = std::net::TcpStream::connect("127.0.0.1:9119").is_ok();
    if !initialized || !is_running {
        // Kill any existing hermes serve process listening on 9119
        let _ = std::process::Command::new("pkill")
            .args(&["-f", "hermes serve --port 9119"])
            .status();
        std::thread::sleep(std::time::Duration::from_millis(200));

        let mut cmd = std::process::Command::new("/Users/matt/.local/bin/hermes");
        cmd.args(&["serve", "--port", "9119"])
           .env("HERMES_DASHBOARD_SESSION_TOKEN", "ai_os_secret_token_123456")
           .stdout(std::process::Stdio::inherit())
           .stderr(std::process::Stdio::inherit());
        let _ = cmd.spawn();
        std::thread::sleep(std::time::Duration::from_millis(800));

        HERMES_INIT.store(true, std::sync::atomic::Ordering::Relaxed);
    }
}

// ---------------------------------------------------------------------------
// Engine PTY management
// ---------------------------------------------------------------------------

pub fn ensure_engine_pty(
    project_path: &str,
    engine: &str,
    app_handle: &tauri::AppHandle,
    session: &mut ProjectSession,
) -> Result<(u32, bool, u16), String> {
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
            Ok((pid, is_new, 0))
        } else {
            Ok((session.claude_pid.unwrap(), false, 0))
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
            Ok((pid, is_new, 0))
        } else {
            Ok((session.agy_pid.unwrap(), false, 0))
        }
    } else if engine == "hermes" {
        ensure_hermes_serve_running();
        Ok((0, false, 9119))
    } else {
        Err(format!("Unknown engine: {}", engine))
    }
}

pub fn ensure_mini_pty(
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

pub fn spawn_fresh_engine(
    project_path: String,
    engine: String,
    thread_id: Option<String>,
    app_handle: tauri::AppHandle,
    state: tauri::State<AppState>,
) -> Result<u32, String> {
    let thread_id_str = thread_id.unwrap_or_default();
    let session_key = format!("{}_{}", project_path, thread_id_str);

    let mut sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    let session = sessions.get_mut(&session_key).ok_or_else(|| "No session found".to_string())?;

    let thread_id_opt = if session.thread_id.is_empty() { None } else { Some(session.thread_id.as_str()) };

    if is_tmux_available() {
        let session_name = get_tmux_session_name(&project_path, &engine, thread_id_opt);
        if has_tmux_session(&session_name) {
            let _ = std::process::Command::new("tmux")
                .args(&["kill-session", "-t", &session_name])
                .status();
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
    } else if engine == "hermes" {
        session.hermes_writer = Some(writer);
        session.hermes_master = Some(master);
        session.hermes_pid = Some(pid);
    }

    trigger_tmux_refresh(&project_path, &engine);

    Ok(pid)
}
