import sys

filepath = "src-tauri/src/main.rs"
with open(filepath, "r") as f:
    content = f.read()

# 1. Update is_engine_running_proc to not use tmux for engine checks
old_proc = """fn is_engine_running_proc(engine: &str, project_path: &str, shell_pid: Option<u32>) -> bool {
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
    };"""

new_proc = """fn is_engine_running_proc(engine: &str, project_path: &str, shell_pid: Option<u32>) -> bool {
    let root_pid = match shell_pid {
        Some(pid) => pid,
        None => return false,
    };"""

content = content.replace(old_proc, new_proc)

# 2. Update trigger_tmux_refresh to only refresh if terminal_type is mini
# wait, trigger_tmux_refresh doesn't take terminal_type. It just does `tmux refresh-client`.
# we can leave it as is, it just refreshes all tmux clients.

# 3. Update spawn_single_pty to only use tmux for "mini"
old_spawn = """    let mut is_new_tmux = false;
    let mut cmd = if is_tmux_available() {
        let session_name = get_tmux_session_name(project_path, terminal_type);"""
new_spawn = """    let mut is_new_tmux = false;
    let mut cmd = if is_tmux_available() && terminal_type == "mini" {
        let session_name = get_tmux_session_name(project_path, terminal_type);"""

content = content.replace(old_spawn, new_spawn)

# 4. Remove tmux kill logic in ensure_engine_pty for "claude" and "agy"
old_ensure_claude = """        if !agy_alive || !client_alive {
            if is_tmux_available() && !agy_alive {
                let session_name = get_tmux_session_name(project_path, "claude");
                if has_tmux_session(&session_name) {
                    let _ = std::process::Command::new("tmux")
                        .args(&["kill-session", "-t", &session_name])
                        .status();
                }
            }
            let (writer, master, pid, is_new) = spawn_single_pty(project_path, "claude", app_handle)?;"""

new_ensure_claude = """        if !agy_alive || !client_alive {
            let (writer, master, pid, is_new) = spawn_single_pty(project_path, "claude", app_handle)?;"""

content = content.replace(old_ensure_claude, new_ensure_claude)

old_ensure_agy = """        if !agy_alive || !client_alive {
            if is_tmux_available() && !agy_alive {
                let session_name = get_tmux_session_name(project_path, "agy");
                if has_tmux_session(&session_name) {
                    let _ = std::process::Command::new("tmux")
                        .args(&["kill-session", "-t", &session_name])
                        .status();
                }
            }
            let (writer, master, pid, is_new) = spawn_single_pty(project_path, "agy", app_handle)?;"""

new_ensure_agy = """        if !agy_alive || !client_alive {
            let (writer, master, pid, is_new) = spawn_single_pty(project_path, "agy", app_handle)?;"""

content = content.replace(old_ensure_agy, new_ensure_agy)

# 5. Fix prepare_spare_engine to not do anything since engine doesn't use tmux
old_spare = """#[tauri::command]
fn prepare_spare_engine(project_path: String, engine: String) -> Result<(), String> {
    if !is_tmux_available() {
        return Ok(());
    }
    let spare_session = format!("{}_spare", get_tmux_session_name(&project_path, &engine));
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
}"""

new_spare = """#[tauri::command]
fn prepare_spare_engine(project_path: String, engine: String) -> Result<(), String> {
    Ok(())
}"""

content = content.replace(old_spare, new_spare)

# 6. Fix spawn_fresh_engine to not kill tmux sessions since we don't use them for engine
old_fresh = """#[tauri::command]
fn spawn_fresh_engine(project_path: String, engine: String, state: tauri::State<AppState>) -> Result<u32, String> {
    let app_handle = state.app_handle.clone();
    let mut sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    let session = sessions.get_mut(&project_path).ok_or_else(|| "No session found".to_string())?;

    if is_tmux_available() {
        let session_name = get_tmux_session_name(&project_path, &engine);
        let spare_session = format!("{}_spare", session_name);

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

    let (writer, master, pid, _) = spawn_single_pty(&project_path, &engine, &app_handle)?;"""

new_fresh = """#[tauri::command]
fn spawn_fresh_engine(project_path: String, engine: String, state: tauri::State<AppState>) -> Result<u32, String> {
    let app_handle = state.app_handle.clone();
    let mut sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    let session = sessions.get_mut(&project_path).ok_or_else(|| "No session found".to_string())?;

    let (writer, master, pid, _) = spawn_single_pty(&project_path, &engine, &app_handle)?;"""

content = content.replace(old_fresh, new_fresh)

# 7. Update close_project_session to only kill "mini" session
old_close = """#[tauri::command]
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
}"""

new_close = """#[tauri::command]
fn close_project_session(project_path: String, state: tauri::State<AppState>) -> Result<(), String> {
    let mut sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    if let Some(_) = sessions.remove(&project_path) {
        let session_name = get_tmux_session_name(&project_path, "mini");
        let _ = std::process::Command::new("tmux")
            .args(&["-u", "kill-session", "-t", &session_name])
            .status();
    }
    Ok(())
}"""

content = content.replace(old_close, new_close)

with open(filepath, "w") as f:
    f.write(content)
print("Updated main.rs successfully")
