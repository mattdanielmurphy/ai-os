use std::path::Path;
use std::fs;

pub fn extract_title_and_snippet(path: &Path) -> Option<(String, String)> {
    let content = fs::read_to_string(path).ok()?;
    let mut title = String::new();
    let mut snippet = String::new();

    for line in content.lines() {
        let trimmed = line.trim();
        if trimmed.starts_with("# ") && title.is_empty() {
            title = trimmed[2..].trim().to_string();
        } else if !trimmed.is_empty() && !trimmed.starts_with('#') && snippet.is_empty() {
            snippet = trimmed.chars().take(200).collect();
        }
        if !title.is_empty() && !snippet.is_empty() {
            break;
        }
    }

    if title.is_empty() {
        if let Some(stem) = path.file_stem().and_then(|s| s.to_str()) {
            title = stem.to_string();
        }
    }

    Some((title, snippet))
}

pub fn get_thread_mtime(path: &Path) -> u64 {
    fs::metadata(path)
        .and_then(|m| m.modified())
        .map(|t| t.duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_secs())
        .unwrap_or(0)
}
