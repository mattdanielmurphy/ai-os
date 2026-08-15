use std::process::Command;
use std::time::Duration;
use wait_timeout::ChildExt;

pub fn execute_command(command: &str, cwd: &str) -> Result<(i32, String, String), String> {
    let mut child = Command::new("sh")
        .arg("-c")
        .arg(command)
        .current_dir(cwd)
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::piped())
        .spawn()
        .map_err(|e| e.to_string())?;

    match child.wait_timeout(Duration::from_secs(60)).map_err(|e| e.to_string())? {
        Some(status) => {
            let exit_code = status.code().unwrap_or(-1);
            let stdout = String::from_utf8_lossy(&std::io::read_to_string(child.stdout.unwrap()).map_err(|e| e.to_string())?).to_string();
            let stderr = String::from_utf8_lossy(&std::io::read_to_string(child.stderr.unwrap()).map_err(|e| e.to_string())?).to_string();
            Ok((exit_code, stdout, stderr))
        }
        None => {
            child.kill().map_err(|e| e.to_string())?;
            Err("Command timed out".to_string())
        }
    }
}
