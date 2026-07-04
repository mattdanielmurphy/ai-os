fn get_tmux_session_name(project_path: &str, terminal_type: &str) -> String {
    format!("ai_os_{}", terminal_type)
}
