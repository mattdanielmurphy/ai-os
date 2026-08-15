use std::fs;
use std::path::{Path, PathBuf};

pub fn is_safe_path(path: &str, project_root: &str) -> bool {
    let base = Path::new(project_root).canonicalize().unwrap_or_else(|_| PathBuf::from(project_root));
    let target = Path::new(path).canonicalize().unwrap_or_else(|_| PathBuf::from(path));
    
    target.starts_with(base)
}

pub fn read_file(path: &str, project_root: &str) -> Result<String, String> {
    if !is_safe_path(path, project_root) {
        return Err("Path traversal detected or unauthorized access".to_string());
    }
    fs::read_to_string(path).map_err(|e| e.to_string())
}

pub fn write_file(path: &str, content: &str, project_root: &str) -> Result<(), String> {
    if !is_safe_path(path, project_root) {
        return Err("Path traversal detected or unauthorized access".to_string());
    }
    fs::write(path, content).map_err(|e| e.to_string())
}

pub fn list_dir(path: &str, project_root: &str) -> Result<Vec<String>, String> {
    if !is_safe_path(path, project_root) {
        return Err("Path traversal detected or unauthorized access".to_string());
    }
    let entries = fs::read_dir(path).map_err(|e| e.to_string())?;
    let names = entries
        .filter_map(|e| e.ok())
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .collect();
    Ok(names)
}
