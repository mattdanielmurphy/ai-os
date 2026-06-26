use portable_pty::{CommandBuilder, NativePtySystem, PtySize, PtySystem};
use std::io::{Read, Write};
use std::sync::{Arc, Mutex};
use tauri::Manager;

// FIX 1: We store a boxed Writer instead of the raw MasterPty
struct AppState {
    pty_writer: Arc<Mutex<Box<dyn Write + Send>>>,
}

#[derive(Clone, serde::Serialize)]
struct Payload {
    data: String,
}

#[tauri::command]
fn write_to_pty(data: String, state: tauri::State<AppState>) -> Result<(), String> {
    let mut writer = state.pty_writer.lock().map_err(|e| e.to_string())?;
    
    // Now write_all and flush will work because the trait bounds are satisfied
    writer.write_all(data.as_bytes()).map_err(|e| e.to_string())?;
    writer.flush().map_err(|e| e.to_string())?;
    
    Ok(())
}

fn main() {
    let pty_system = NativePtySystem::default();

    // FIX 2: openpicker was a hallucination. The correct method is openpty.
    let pair = pty_system.openpty(PtySize {
        rows: 24,
        cols: 80,
        pixel_width: 0,
        pixel_height: 0,
    }).expect("Failed to open PTY");

    let cmd = CommandBuilder::new("/bin/zsh");
    let _child = pair.slave.spawn_command(cmd).expect("Failed to spawn shell");

    // FIX 3: We must clone the reader and writer out of the master PTY 
    let reader = pair.master.try_clone_reader().expect("Failed to clone reader");
    let writer = pair.master.take_writer().expect("Failed to take writer");

    // Store the writer in our thread-safe state
    let pty_writer = Arc::new(Mutex::new(writer));

    tauri::Builder::default()
        .manage(AppState {
            pty_writer: pty_writer.clone(),
        })
        .setup(|app| {
            let app_handle = app.handle();
            
            // Spawn the read loop in a background thread
            std::thread::spawn(move || {
                let mut reader = reader;
                let mut buf = [0u8; 1024];
                loop {
                    match reader.read(&mut buf) {
                        Ok(n) if n > 0 => {
                            let data = String::from_utf8_lossy(&buf[..n]).to_string();
                            // emit_all works here because we are on Tauri v1
                            app_handle.emit_all("pty-output", Payload { data }).ok();
                        }
                        _ => break,
                    }
                }
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![write_to_pty])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}