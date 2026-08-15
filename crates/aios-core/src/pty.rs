use std::path::PathBuf;

pub fn get_ai_os_home() -> PathBuf {
    std::env::var("AI_OS_HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|_| {
            let home = std::env::var("HOME").unwrap_or_else(|_| "/Users/matt".to_string());
            PathBuf::from(home).join("projects").join("ai-os")
        })
}
