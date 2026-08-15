use crate::shell_bridge;

pub async fn get_project_snapshot(project_root: &str) -> Result<String, String> {
    let (_, branch, _) = shell_bridge::execute_command("git branch --show-current", project_root).await.unwrap_or((-1, "unknown".to_string(), "".to_string()));
    let (_, status, _) = shell_bridge::execute_command("git status --short", project_root).await.unwrap_or((-1, "".to_string(), "".to_string()));
    
    let snapshot = format!(
        "### Project Context Snapshot\n- **Project Root**: `{}`\n- **Git Branch**: `{}`\n- **Git Status**:\n```\n{}\n```\n",
        project_root,
        branch.trim(),
        if status.trim().is_empty() { "clean" } else { status.trim() }
    );

    Ok(snapshot)
}

