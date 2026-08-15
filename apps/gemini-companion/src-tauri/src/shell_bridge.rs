use std::time::Duration;
use tokio::time::timeout;

pub async fn execute_command(command: &str, cwd: &str) -> Result<(i32, String, String), String> {
    let mut cmd = tokio::process::Command::new("sh");
    cmd.arg("-c").arg(command);
    if !cwd.is_empty() {
        cmd.current_dir(cwd);
    }

    let output_future = cmd.output();
    match timeout(Duration::from_secs(60), output_future).await {
        Ok(Ok(output)) => {
            let exit_code = output.status.code().unwrap_or(-1);
            let stdout = String::from_utf8_lossy(&output.stdout).to_string();
            let stderr = String::from_utf8_lossy(&output.stderr).to_string();
            Ok((exit_code, stdout, stderr))
        }
        Ok(Err(e)) => Err(format!("Command execution failed: {}", e)),
        Err(_) => Err("Command timed out after 60 seconds".to_string()),
    }
}
