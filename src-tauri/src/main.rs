use portable_pty::{CommandBuilder, MasterPty, NativePtySystem, PtySize, PtySystem};
use std::io::{Read, Write};
use std::sync::{Arc, Mutex};
use tauri::Manager;

// 1. Add pty_master to our AppState
struct AppState {
    pty_writer: Arc<Mutex<Box<dyn Write + Send>>>,
    pty_master: Arc<Mutex<Box<dyn MasterPty + Send>>>,
    shell_pid: u32,
}

#[derive(Clone, serde::Serialize)]
struct Payload {
    data: String,
}

#[tauri::command]
fn write_to_pty(data: String, state: tauri::State<AppState>) -> Result<(), String> {
    let mut writer = state.pty_writer.lock().map_err(|e| e.to_string())?;
    writer.write_all(data.as_bytes()).map_err(|e| e.to_string())?;
    writer.flush().map_err(|e| e.to_string())?;
    Ok(())
}

// 2. Add the resize command
#[tauri::command]
fn resize_pty(rows: u16, cols: u16, state: tauri::State<AppState>) -> Result<(), String> {
    let master = state.pty_master.lock().map_err(|e| e.to_string())?;
    master.resize(PtySize {
        rows,
        cols,
        pixel_width: 0,
        pixel_height: 0,
    }).map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
fn is_engine_running(engine: String, state: tauri::State<AppState>) -> Result<bool, String> {
    let shell_pid = state.shell_pid;
    
    // Run `ps -A -o ppid,pid,args`
    let output = std::process::Command::new("ps")
        .args(&["-A", "-o", "ppid,pid,args"])
        .output()
        .map_err(|e| e.to_string())?;
        
    let stdout = String::from_utf8_lossy(&output.stdout);
    
    // Parse the process list
    use std::collections::HashMap;
    let mut parent_to_children: HashMap<u32, Vec<(u32, String)>> = HashMap::new();
    
    for line in stdout.lines().skip(1) {
        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.len() >= 3 {
            if let (Ok(ppid), Ok(pid)) = (parts[0].parse::<u32>(), parts[1].parse::<u32>()) {
                let args = parts[2..].join(" ");
                parent_to_children.entry(ppid).or_default().push((pid, args));
            }
        }
    }
    
    // Perform BFS starting from shell_pid to find any descendant process that matches the engine name
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
    let pty_system = NativePtySystem::default();
    let pair = pty_system.openpty(PtySize {
        rows: 24,
        cols: 80,
        pixel_width: 0,
        pixel_height: 0,
    }).expect("Failed to open PTY");

    let cmd = CommandBuilder::new("/bin/zsh");
    let _child = pair.slave.spawn_command(cmd).expect("Failed to spawn shell");
    let shell_pid = _child.process_id().unwrap_or(0);

    let reader = pair.master.try_clone_reader().expect("Failed to clone reader");
    let writer = pair.master.take_writer().expect("Failed to take writer");

    // 3. Move the master into a thread-safe mutex
    let pty_writer = Arc::new(Mutex::new(writer));
    let pty_master = Arc::new(Mutex::new(pair.master));

    tauri::Builder::default()
        .manage(AppState {
            pty_writer,
            pty_master,
            shell_pid,
        })
        .setup(|app| {
            let app_handle = app.handle();
            std::thread::spawn(move || {
                let mut reader = reader;
                let mut buf = [0u8; 1024];
                loop {
                    match reader.read(&mut buf) {
                        Ok(n) if n > 0 => {
                            let data = String::from_utf8_lossy(&buf[..n]).to_string();
                            app_handle.emit_all("pty-output", Payload { data }).ok();
                        }
                        _ => break,
                    }
                }
            });
            Ok(())
        })
        // 4. Register the new command here
        .invoke_handler(tauri::generate_handler![write_to_pty, resize_pty, is_engine_running])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}