// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::sync::{Arc, Mutex};
use std::io::Write;
use portable_pty::{native_pty_system, Child, CommandBuilder, MasterPty, PtySize};
use serde::Serialize;
use tauri::{Manager, State};

struct AppState {
    master_pty: Arc<Mutex<Box<dyn MasterPty + Send + Sync>>>,
    // Keep child alive so it doesn't get dropped immediately
    _child: Mutex<Box<dyn Child + Send + Sync>>,
}

#[derive(Clone, Serialize)]
struct Payload {
    data: String,
}

#[tauri::command]
fn write_to_pty(data: String, state: State<'_, AppState>) -> Result<(), String> {
    let mut master = state.master_pty.lock().map_err(|e| e.to_string())?;
    master.write_all(data.as_bytes()).map_err(|e| e.to_string())?;
    master.flush().map_err(|e| e.to_string())?;
    Ok(())
}

fn main() {
    // Initialize PTY system
    let pty_system = native_pty_system();
    let master = pty_system
        .openpicker(PtySize {
            rows: 24,
            cols: 80,
            pixel_width: 0,
            pixel_height: 0,
        })
        .expect("failed to open pty");

    // Spawn macOS default zsh
    let mut cmd = CommandBuilder::new("/bin/zsh");
    // Ensure we start in the user home or projects directory to be clean
    cmd.cwd(std::env::current_dir().unwrap_or_else(|_| std::path::PathBuf::from("/Users/matthewmurphy/projects/ai-os")));
    let child = master.spawn_reader_and_writer(cmd).expect("failed to spawn shell");

    let master_writer = master.try_clone_writer().expect("failed to clone master writer");
    let mut reader = master.try_clone_reader().expect("failed to clone master reader");

    let app_state = AppState {
        master_pty: Arc::new(Mutex::new(master_writer)),
        _child: Mutex::new(child),
    };

    tauri::Builder::default()
        .manage(app_state)
        .invoke_handler(tauri::generate_handler![write_to_pty])
        .setup(|app| {
            let app_handle = app.handle();
            
            // Spawn background thread to read from PTY
            std::thread::spawn(move || {
                let mut buf = [0u8; 1024];
                loop {
                    match reader.read(&mut buf) {
                        Ok(n) => {
                            if n == 0 {
                                break;
                            }
                            let data = String::from_utf8_lossy(&buf[..n]).to_string();
                            let _ = app_handle.emit_all("pty-output", Payload { data });
                        }
                        Err(_) => {
                            break;
                        }
                    }
                }
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
