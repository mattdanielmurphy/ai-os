use crate::shell_bridge;

pub fn get_project_snapshot(project_root: &str) -> Result<String, String> {
    let mut snapshot = String::from("# Project Context Snapshot\n\n");
    
    // Git branch
    let (_, branch, _) = shell_bridge::execute_command("git branch --show-current", project_root)?;
    snapshot.push_str(&format!("## Branch\n{}\n\n", branch.trim()));
    
    // Git status
    let (_, status, _) = shell_bridge::execute_command("git status --short", project_root)?;
    snapshot.push_str(&format!("## Git Status\n```\n{}\n```\n\n", status));
    
    // Directory structure
    let (_, structure, _) = shell_bridge::execute_command("ls -R", project_root)?;
    snapshot.push_str(&format!("## Directory Structure\n```\n{}\n```\n", structure));
    
    Ok(snapshot)
}
