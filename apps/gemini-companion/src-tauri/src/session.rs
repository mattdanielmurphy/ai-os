use std::io::Write;
use tauri::Manager;

use crate::types::{AppState, PauseStatusPayload, ProjectSession, SwitchResult};
use crate::pty;

// ---------------------------------------------------------------------------
// Session management
// ---------------------------------------------------------------------------

#[tauri::command]
pub fn switch_active_project(
    project_path: String,
    engine: String,
    thread_id: Option<String>,
    state: tauri::State<AppState>,
) -> Result<SwitchResult, String> {
    let app_handle = state.app_handle.clone();
    let thread_id_str = thread_id.unwrap_or_default();
    let session_key = format!("{}_{}", project_path, thread_id_str);

    let mut sessions = state.sessions.lock().map_err(|e| e.to_string())?;

    // Evict old sessions if we have too many
    if sessions.len() >= 20 && !sessions.contains_key(&session_key) {
        let mut keys_to_evict = Vec::new();
        let mut sorted_sessions: Vec<_> = sessions
            .iter()
            .map(|(k, s)| (k.clone(), s.last_accessed))
            .collect();
        sorted_sessions.sort_by_key(|&(_, t)| t);

        let num_to_evict = (sessions.len() - 15).min(sorted_sessions.len());
        for i in 0..num_to_evict {
            keys_to_evict.push(sorted_sessions[i].0.clone());
        }

        for k in keys_to_evict {
            if let Some(old_session) = sessions.remove(&k) {
                if let Some(pid) = old_session.claude_pid {
                    let _ = std::process::Command::new("kill")
                        .arg("-9")
                        .arg(pid.to_string())
                        .status();
                }
                if let Some(pid) = old_session.agy_pid {
                    let _ = std::process::Command::new("kill")
                        .arg("-9")
                        .arg(pid.to_string())
                        .status();
                }
                if let Some(pid) = old_session.hermes_pid {
                    let _ = std::process::Command::new("kill")
                        .arg("-9")
                        .arg(pid.to_string())
                        .status();
                }
                let _ = std::process::Command::new("kill")
                    .arg("-9")
                    .arg(old_session.mini_pid.to_string())
                    .status();

                if pty::is_tmux_available() {
                    let thread_id_opt = if old_session.thread_id.is_empty() {
                        None
                    } else {
                        Some(old_session.thread_id.as_str())
                    };
                    let cl_session = pty::get_tmux_session_name(
                        &old_session.project_path,
                        "claude",
                        thread_id_opt,
                    );
                    let ag_session = pty::get_tmux_session_name(
                        &old_session.project_path,
                        "agy",
                        thread_id_opt,
                    );
                    let he_session = pty::get_tmux_session_name(
                        &old_session.project_path,
                        "hermes",
                        thread_id_opt,
                    );
                    let mi_session = pty::get_tmux_session_name(
                        &old_session.project_path,
                        "mini",
                        None,
                    );

                    let _ = std::process::Command::new("tmux")
                        .args(&["-u", "kill-session", "-t", &cl_session])
                        .status();
                    let _ = std::process::Command::new("tmux")
                        .args(&["-u", "kill-session", "-t", &ag_session])
                        .status();
                    let _ = std::process::Command::new("tmux")
                        .args(&["-u", "kill-session", "-t", &he_session])
                        .status();
                    let _ = std::process::Command::new("tmux")
                        .args(&["-u", "kill-session", "-t", &mi_session])
                        .status();
                }
            }
        }
    }

    let is_new_proj = !sessions.contains_key(&session_key);
    if is_new_proj {
        if engine == "hermes" {
            pty::ensure_hermes_serve_running();
            let app_handle_clone = app_handle.clone();
            let path_clone = project_path.clone();
            let mini_thread = std::thread::spawn(move || {
                pty::spawn_single_pty(&path_clone, "mini", &app_handle_clone, None)
            });
            let (mini_writer, mini_master, mini_pid, _) = mini_thread
                .join()
                .map_err(|_| "Failed to join mini PTY spawn thread".to_string())??;

            let session = ProjectSession {
                claude_writer: None,
                claude_master: None,
                claude_pid: None,
                agy_writer: None,
                agy_master: None,
                agy_pid: None,
                hermes_writer: None,
                hermes_master: None,
                hermes_pid: None,
                mini_writer,
                mini_master,
                mini_pid,
                project_path: project_path.clone(),
                thread_id: thread_id_str.clone(),
                last_accessed: std::time::SystemTime::now(),
            };

            sessions.insert(session_key.clone(), session);

            let mut active = state.active_project.lock().map_err(|e| e.to_string())?;
            *active = Some(project_path.clone());

            return Ok(SwitchResult {
                shell_pid: 0,
                is_new_session: true,
                hermes_ws_port: 9119,
            });
        }

        // Spawn mini and engine PTYs in parallel
        let app_handle_clone1 = app_handle.clone();
        let app_handle_clone2 = app_handle.clone();
        let path_clone1 = project_path.clone();
        let path_clone2 = project_path.clone();
        let engine_clone = engine.clone();
        let thread_id_clone1 = thread_id_str.clone();

        let mini_thread = std::thread::spawn(move || {
            pty::spawn_single_pty(&path_clone1, "mini", &app_handle_clone1, None)
        });
        let engine_thread = std::thread::spawn(move || {
            let thread_id_opt = if thread_id_clone1.is_empty() {
                None
            } else {
                Some(thread_id_clone1.as_str())
            };
            pty::spawn_single_pty(
                &path_clone2,
                &engine_clone,
                &app_handle_clone2,
                thread_id_opt,
            )
        });

        let (mini_writer, mini_master, mini_pid, _) = mini_thread
            .join()
            .map_err(|_| "Failed to join mini PTY spawn thread".to_string())??;
        let (engine_writer, engine_master, engine_pid, is_new_session) = engine_thread
            .join()
            .map_err(|_| "Failed to join engine PTY spawn thread".to_string())??;

        let mut session = ProjectSession {
            claude_writer: None,
            claude_master: None,
            claude_pid: None,
            agy_writer: None,
            agy_master: None,
            agy_pid: None,
            hermes_writer: None,
            hermes_master: None,
            hermes_pid: None,
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
        } else if engine == "hermes" {
            session.hermes_writer = Some(engine_writer);
            session.hermes_master = Some(engine_master);
            session.hermes_pid = Some(engine_pid);
        }

        sessions.insert(session_key.clone(), session);

        let mut active = state.active_project.lock().map_err(|e| e.to_string())?;
        *active = Some(project_path.clone());

        pty::trigger_tmux_refresh(&project_path, &engine);

        return Ok(SwitchResult {
            shell_pid: engine_pid,
            is_new_session,
            hermes_ws_port: 0,
        });
    }

    let session = sessions.get_mut(&session_key).unwrap();
    session.last_accessed = std::time::SystemTime::now();
    let (shell_pid, is_new_session, hermes_ws_port) =
        pty::ensure_engine_pty(&project_path, &engine, &app_handle, session)?;
    pty::ensure_mini_pty(&project_path, &app_handle, session)?;

    let mut active = state.active_project.lock().map_err(|e| e.to_string())?;
    *active = Some(project_path.clone());

    pty::trigger_tmux_refresh(&project_path, &engine);

    Ok(SwitchResult {
        shell_pid,
        is_new_session,
        hermes_ws_port,
    })
}

#[tauri::command]
pub fn close_project_session(
    project_path: String,
    state: tauri::State<AppState>,
) -> Result<(), String> {
    let mut sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    let prefix = format!("{}_", project_path);
    let keys_to_remove: Vec<String> = sessions
        .keys()
        .filter(|k| k.starts_with(&prefix))
        .cloned()
        .collect();

    for key in keys_to_remove {
        if let Some(session) = sessions.remove(&key) {
            let thread_id_opt = if session.thread_id.is_empty() {
                None
            } else {
                Some(session.thread_id.as_str())
            };
            let cl_session =
                pty::get_tmux_session_name(&project_path, "claude", thread_id_opt);
            let ag_session =
                pty::get_tmux_session_name(&project_path, "agy", thread_id_opt);
            let mi_session =
                pty::get_tmux_session_name(&project_path, "mini", None);

            let _ = std::process::Command::new("tmux")
                .args(&["-u", "kill-session", "-t", &cl_session])
                .status();
            let _ = std::process::Command::new("tmux")
                .args(&["-u", "kill-session", "-t", &ag_session])
                .status();
            let _ = std::process::Command::new("tmux")
                .args(&["-u", "kill-session", "-t", &mi_session])
                .status();
        }
    }
    Ok(())
}

// ---------------------------------------------------------------------------
// PTY I/O commands
// ---------------------------------------------------------------------------

#[tauri::command]
pub fn write_to_pty(
    data: String,
    project_path: String,
    terminal_type: String,
    thread_id: Option<String>,
    state: tauri::State<AppState>,
) -> Result<(), String> {
    if terminal_type == "hermes" {
        return Ok(());
    }

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
pub fn resize_pty(
    rows: u16,
    cols: u16,
    project_path: String,
    terminal_type: String,
    thread_id: Option<String>,
    state: tauri::State<AppState>,
) -> Result<(), String> {
    let thread_id_str = thread_id.unwrap_or_default();
    let session_key = format!("{}_{}", project_path, thread_id_str);

    let sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    if let Some(session) = sessions.get(&session_key) {
        let size = portable_pty::PtySize {
            rows,
            cols,
            pixel_width: 0,
            pixel_height: 0,
        };
        if terminal_type == "mini" {
            session.mini_master.resize(size).map_err(|e| e.to_string())?;
        } else {
            if let Some(ref master) = session.claude_master {
                let _ = master.resize(size);
            }
            if let Some(ref master) = session.agy_master {
                let _ = master.resize(size);
            }
        }
        Ok(())
    } else {
        Err(format!("No PTY session found for project: {}", project_path))
    }
}

#[tauri::command]
pub fn is_engine_running(
    engine: String,
    project_path: String,
    thread_id: Option<String>,
    state: tauri::State<AppState>,
) -> Result<bool, String> {
    let thread_id_str = thread_id.unwrap_or_default();
    let session_key = format!("{}_{}", project_path, thread_id_str);

    let sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    let shell_pid = match sessions.get(&session_key) {
        Some(s) => {
            if engine == "claude" {
                s.claude_pid
            } else if engine == "hermes" {
                s.hermes_pid
            } else {
                s.agy_pid
            }
        }
        None => return Ok(false),
    };
    drop(sessions);

    let thread_id_opt = if thread_id_str.is_empty() {
        None
    } else {
        Some(thread_id_str.as_str())
    };
    Ok(pty::is_engine_running_proc(
        &engine,
        &project_path,
        thread_id_opt,
        shell_pid,
    ))
}

// ---------------------------------------------------------------------------
// Process pause/resume
// ---------------------------------------------------------------------------

#[tauri::command]
pub fn toggle_process_pause(
    project_path: String,
    engine: String,
    pause: bool,
    thread_id: Option<String>,
    state: tauri::State<AppState>,
) -> Result<(), String> {
    let thread_id_str = thread_id.unwrap_or_default();
    let session_key = format!("{}_{}", project_path, thread_id_str);

    let sessions = state.sessions.lock().map_err(|e| e.to_string())?;
    let session = sessions
        .get(&session_key)
        .ok_or_else(|| format!("No active session for key: {}", session_key))?;
    let shell_pid = if engine == "claude" {
        session.claude_pid
    } else if engine == "hermes" {
        session.hermes_pid
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

    let signal = if pause { "-TSTP" } else { "-CONT" };
    std::process::Command::new("kill")
        .args(&[signal, &shell_pid.to_string()])
        .status()
        .map_err(|e| e.to_string())?;

    state.app_handle.emit_all(
        "pause-status",
        PauseStatusPayload {
            project_path,
            status: if pause { "Paused".to_string() } else { "Running".to_string() },
        },
    ).ok();

    Ok(())
}

// ---------------------------------------------------------------------------
// Misc commands (still session-related)
// ---------------------------------------------------------------------------

#[tauri::command]
pub async fn select_directory() -> Result<Option<String>, String> {
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
pub fn create_new_project(name: String, git_repo_name: String) -> Result<String, String> {
    let home = std::env::var("HOME").map_err(|_| "Could not find HOME directory".to_string())?;
    let projects_dir = std::path::Path::new(&home).join("projects");
    if !projects_dir.exists() {
        std::fs::create_dir_all(&projects_dir)
            .map_err(|e| format!("Failed to create projects directory: {}", e))?;
    }

    let project_path = projects_dir.join(&name);
    if project_path.exists() {
        return Err("Project directory already exists".to_string());
    }

    std::fs::create_dir_all(&project_path)
        .map_err(|e| format!("Failed to create project directory: {}", e))?;

    // git init
    let output = std::process::Command::new("git")
        .arg("init")
        .current_dir(&project_path)
        .output()
        .map_err(|e| format!("Failed to run git init: {}", e))?;
    if !output.status.success() {
        return Err(format!(
            "git init failed: {}",
            String::from_utf8_lossy(&output.stderr)
        ));
    }

    std::fs::write(project_path.join("README.md"), format!("# {}\n", name))
        .map_err(|e| format!("Failed to write README.md: {}", e))?;

    let output = std::process::Command::new("git")
        .args(&["add", "README.md"])
        .current_dir(&project_path)
        .output()
        .map_err(|e| format!("Failed to run git add: {}", e))?;
    if !output.status.success() {
        return Err(format!(
            "git add failed: {}",
            String::from_utf8_lossy(&output.stderr)
        ));
    }

    let output = std::process::Command::new("git")
        .args(&["commit", "-m", "Initial commit"])
        .current_dir(&project_path)
        .output()
        .map_err(|e| format!("Failed to run git commit: {}", e))?;
    if !output.status.success() {
        return Err(format!(
            "git commit failed: {}",
            String::from_utf8_lossy(&output.stderr)
        ));
    }

    let output = std::process::Command::new("gh")
        .args(&[
            "repo",
            "create",
            &git_repo_name,
            "--private",
            "--source=.",
            "--remote=origin",
            "--push",
        ])
        .current_dir(&project_path)
        .output()
        .map_err(|e| format!("Failed to run gh repo create: {}", e))?;
    if !output.status.success() {
        return Err(format!(
            "gh repo create failed: {}",
            String::from_utf8_lossy(&output.stderr)
        ));
    }

    Ok(project_path.to_string_lossy().to_string())
}

#[tauri::command]
pub fn copy_tmux_selection(
    project_path: String,
    terminal_type: String,
    thread_id: Option<String>,
) -> Result<(), String> {
    if pty::is_tmux_available() {
        let thread_id_opt = thread_id.as_deref();
        let session_name =
            pty::get_tmux_session_name(&project_path, &terminal_type, thread_id_opt);
        let status = std::process::Command::new("tmux")
            .args(&[
                "-u",
                "send-keys",
                "-t",
                &session_name,
                "-X",
                "copy-pipe-and-cancel",
                "pbcopy",
            ])
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
pub fn open_path(path: String) -> Result<(), String> {
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
pub fn get_initial_project() -> Option<String> {
    std::env::var("AIOS_INITIAL_PROJECT").ok()
}

#[tauri::command]
pub fn save_prompt_draft(project_path: String, content: String) -> Result<(), String> {
    let home = std::env::var("HOME").map_err(|_| "Could not find HOME directory".to_string())?;
    let drafts_dir = std::path::Path::new(&home)
        .join(".gemini")
        .join("antigravity-cli")
        .join("drafts");

    if !drafts_dir.exists() {
        std::fs::create_dir_all(&drafts_dir)
            .map_err(|e| format!("Failed to create drafts directory: {}", e))?;
    }

    let safe_filename = project_path.replace("/", "_").replace("\\", "_").replace(":", "_")
        + ".txt";

    let draft_path = drafts_dir.join(safe_filename);
    std::fs::write(draft_path, content)
        .map_err(|e| format!("Failed to write prompt draft: {}", e))?;
    Ok(())
}

#[tauri::command]
pub fn load_prompt_draft(project_path: String) -> Result<String, String> {
    let home = std::env::var("HOME").map_err(|_| "Could not find HOME directory".to_string())?;
    let drafts_dir = std::path::Path::new(&home)
        .join(".gemini")
        .join("antigravity-cli")
        .join("drafts");

    let safe_filename = project_path.replace("/", "_").replace("\\", "_").replace(":", "_")
        + ".txt";

    let draft_path = drafts_dir.join(safe_filename);
    if draft_path.exists() {
        std::fs::read_to_string(draft_path)
            .map_err(|e| format!("Failed to read prompt draft: {}", e))
    } else {
        Ok(String::new())
    }
}

#[tauri::command]
pub fn open_devtools(window: tauri::Window) {
    window.open_devtools();
}

#[tauri::command]
pub fn refresh_tmux_session(project_path: String, engine: String) -> Result<(), String> {
    pty::trigger_tmux_refresh(&project_path, &engine);
    if pty::is_tmux_available() {
        let _ = std::process::Command::new("tmux")
            .args(&["-u", "refresh-client"])
            .status();
    }
    Ok(())
}

#[tauri::command]
pub fn ensure_hermes_running() {
    pty::ensure_hermes_serve_running();
}

// ---------------------------------------------------------------------------
// Quota
// ---------------------------------------------------------------------------

#[tauri::command]
pub async fn get_quota(state: tauri::State<'_, AppState>) -> Result<String, String> {
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
        paths.sort();

        for path in paths.iter().rev().take(10) {
            if let Ok(content) = std::fs::read_to_string(path) {
                for line in content.lines().rev() {
                    if let Some(idx) = line.find("authenticated successfully as ") {
                        let email =
                            line[idx + "authenticated successfully as ".len()..].trim();
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

            let mut last_acct =
                state.last_active_account.lock().map_err(|e| e.to_string())?;
            if let Some(ref last) = *last_acct {
                if last != email {
                    println!(
                        "[DEBUG] Account changed from {} to {}. Clearing PTY sessions.",
                        last, email
                    );

                    let mut sessions =
                        state.sessions.lock().map_err(|e| e.to_string())?;
                    sessions.clear();

                    if pty::is_tmux_available() {
                        if let Ok(output) = std::process::Command::new("tmux")
                            .args(&["list-sessions", "-F", "#S"])
                            .output()
                        {
                            let sessions_str =
                                String::from_utf8_lossy(&output.stdout);
                            for line in sessions_str.lines() {
                                let session_name = line.trim();
                                if session_name.starts_with("ai_os_") {
                                    let _ = std::process::Command::new("tmux")
                                        .args(&["kill-session", "-t", session_name])
                                        .status();
                                }
                            }
                        }
                    }

                    let _ = state
                        .app_handle
                        .emit_all("account-changed", email.clone());
                }
            }
            *last_acct = Some(email.clone());
        }
    }

    let output = cmd.arg("-j").output().map_err(|e| e.to_string())?;
    Ok(String::from_utf8_lossy(&output.stdout).to_string())
}
