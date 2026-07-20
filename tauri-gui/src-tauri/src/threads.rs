use std::collections::HashMap;

use crate::types::{CachedThreadInfo, ThreadLog, ThreadSearchResult};

// ---------------------------------------------------------------------------
// Static caches
// ---------------------------------------------------------------------------

static CHILD_TO_PARENT_CACHE: std::sync::OnceLock<std::sync::Mutex<HashMap<String, String>>> =
    std::sync::OnceLock::new();
static THREAD_INFO_CACHE: std::sync::OnceLock<std::sync::Mutex<HashMap<String, CachedThreadInfo>>> =
    std::sync::OnceLock::new();

// ---------------------------------------------------------------------------
// Date helpers
// ---------------------------------------------------------------------------

fn is_leap_year(year: u64) -> bool {
    (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0)
}

fn parse_rfc3339_to_unix(s: &str) -> Option<u64> {
    if s.len() < 19 {
        return None;
    }
    let year: u64 = s[0..4].parse().ok()?;
    let month: u64 = s[5..7].parse().ok()?;
    let day: u64 = s[8..10].parse().ok()?;
    let hour: u64 = s[11..13].parse().ok()?;
    let minute: u64 = s[14..16].parse().ok()?;
    let second: u64 = s[17..19].parse().ok()?;

    let month_days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    let mut days = 0;
    for y in 1970..year {
        days += if is_leap_year(y) { 366 } else { 365 };
    }
    for m in 1..month {
        if m == 2 && is_leap_year(year) {
            days += 29;
        } else {
            days += month_days[m as usize];
        }
    }
    days += day - 1;
    let mut total_seconds = days * 86400 + hour * 3600 + minute * 60 + second;

    if s.len() > 19 {
        let remainder = &s[19..];
        if let Some(plus_pos) = remainder.find('+') {
            let offset_part = &remainder[plus_pos + 1..];
            if offset_part.len() >= 5 {
                let off_h: u64 = offset_part[0..2].parse().unwrap_or(0);
                let off_m: u64 = offset_part[3..5].parse().unwrap_or(0);
                total_seconds = total_seconds.saturating_sub(off_h * 3600 + off_m * 60);
            }
        } else if let Some(minus_pos) = remainder.find('-') {
            let offset_part = &remainder[minus_pos + 1..];
            if offset_part.len() >= 5 {
                let off_h: u64 = offset_part[0..2].parse().unwrap_or(0);
                let off_m: u64 = offset_part[3..5].parse().unwrap_or(0);
                total_seconds = total_seconds.saturating_add(off_h * 3600 + off_m * 60);
            }
        }
    }

    Some(total_seconds)
}

fn get_last_message_timestamp(filepath: &std::path::Path) -> Option<u64> {
    use std::io::{BufRead, BufReader};

    let file = std::fs::File::open(filepath).ok()?;
    let reader = BufReader::new(file);
    let mut last_timestamp = None;

    for line in reader.lines() {
        if let Ok(line_str) = line {
            if let Ok(obj) = serde_json::from_str::<serde_json::Value>(&line_str) {
                if let Some(created_at) = obj.get("created_at").and_then(|v| v.as_str()) {
                    if let Some(ts) = parse_rfc3339_to_unix(created_at) {
                        last_timestamp = Some(ts);
                    }
                }
            }
        }
    }
    last_timestamp
}

// ---------------------------------------------------------------------------
// Thread chain resolution
// ---------------------------------------------------------------------------

fn get_child_to_parent_map(brain_dir: &std::path::Path) -> HashMap<String, String> {
    let cache_mutex =
        CHILD_TO_PARENT_CACHE.get_or_init(|| std::sync::Mutex::new(HashMap::new()));
    let mut cache = cache_mutex.lock().unwrap();

    if let Ok(entries) = std::fs::read_dir(brain_dir) {
        for entry in entries {
            if let Ok(entry) = entry {
                let path = entry.path();
                if path.is_dir() {
                    if let Some(thread_id) = path.file_name().map(|n| n.to_string_lossy().to_string())
                    {
                        if cache.contains_key(&thread_id) {
                            continue;
                        }
                        let transcript_path = path
                            .join(".system_generated")
                            .join("logs")
                            .join("transcript.jsonl");
                        if transcript_path.exists() {
                            use std::io::Read;
                            if let Ok(mut file) = std::fs::File::open(&transcript_path) {
                                let mut buffer = vec![0; 4096];
                                if let Ok(n) = file.read(&mut buffer) {
                                    let content = String::from_utf8_lossy(&buffer[..n]);
                                    if let Some(pos) = content.find(
                                        "Continuing conversation from history (Thread ID:",
                                    ) {
                                        let after = &content[pos
                                            + "Continuing conversation from history (Thread ID:"
                                                .len()..];
                                        if let Some(end_pos) = after.find(')') {
                                            let parent_id =
                                                after[..end_pos].trim().to_string();
                                            if parent_id
                                                .chars()
                                                .all(|c| c.is_alphanumeric() || c == '-')
                                            {
                                                cache
                                                    .insert(thread_id.clone(), parent_id);
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    cache.clone()
}

fn get_root_thread_id(
    thread_id: &str,
    child_to_parent: &HashMap<String, String>,
) -> String {
    let mut current = thread_id.to_string();
    let mut visited = std::collections::HashSet::new();
    visited.insert(current.clone());
    while let Some(parent) = child_to_parent.get(&current) {
        if visited.contains(parent) {
            break;
        }
        current = parent.clone();
        visited.insert(current.clone());
    }
    current
}

fn get_thread_chain(
    root_id: &str,
    child_to_parent: &HashMap<String, String>,
    thread_mtimes: &HashMap<String, u64>,
) -> Vec<String> {
    let mut chain = Vec::new();
    for thread_id in thread_mtimes.keys() {
        if get_root_thread_id(thread_id, child_to_parent) == root_id {
            chain.push(thread_id.clone());
        }
    }
    chain.sort_by_key(|id| thread_mtimes.get(id).cloned().unwrap_or(0));
    chain
}

fn scan_brain_threads(
    brain_dir: &std::path::Path,
) -> (HashMap<String, String>, HashMap<String, u64>) {
    let child_to_parent = get_child_to_parent_map(brain_dir);
    let mut thread_mtimes = HashMap::new();

    if let Ok(entries) = std::fs::read_dir(brain_dir) {
        for entry in entries {
            if let Ok(entry) = entry {
                let path = entry.path();
                if path.is_dir() {
                    if let Some(thread_id) =
                        path.file_name().map(|n| n.to_string_lossy().to_string())
                    {
                        let transcript_path = path
                            .join(".system_generated")
                            .join("logs")
                            .join("transcript.jsonl");
                        if transcript_path.exists() {
                            if let Ok(metadata) = std::fs::metadata(&transcript_path) {
                                let mtime = metadata
                                    .modified()
                                    .and_then(|t| {
                                        t.duration_since(std::time::UNIX_EPOCH)
                                            .map_err(|e| std::io::Error::new(
                                                std::io::ErrorKind::Other,
                                                e,
                                            ))
                                    })
                                    .map(|d| d.as_secs())
                                    .unwrap_or(0);
                                thread_mtimes.insert(thread_id.clone(), mtime);
                            }
                        }
                    }
                }
            }
        }
    }

    (child_to_parent, thread_mtimes)
}

// ---------------------------------------------------------------------------
// Thread info caching
// ---------------------------------------------------------------------------

fn get_cached_thread_info(
    latest_filepath: &std::path::Path,
    latest_thread_id: &str,
) -> Option<CachedThreadInfo> {
    let metadata = std::fs::metadata(latest_filepath).ok()?;
    let mtime = metadata
        .modified()
        .and_then(|t| {
            t.duration_since(std::time::UNIX_EPOCH)
                .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))
        })
        .map(|d| d.as_secs())
        .unwrap_or(0);
    let size = metadata.len();

    let cache_mutex =
        THREAD_INFO_CACHE.get_or_init(|| std::sync::Mutex::new(HashMap::new()));
    {
        let cache = cache_mutex.lock().unwrap();
        if let Some(info) = cache.get(latest_thread_id) {
            if info.mtime == mtime && info.size == size {
                return Some(info.clone());
            }
        }
    }

    // Cache miss or modified file
    use std::io::Read;
    let file = std::fs::File::open(latest_filepath).ok()?;
    let mut buffer = Vec::new();
    let _ = file.take(131072).read_to_end(&mut buffer);
    let content = String::from_utf8_lossy(&buffer);
    let project_path = detect_project_path(&content);
    let mut title = latest_thread_id.to_string();
    let mut snippet = String::new();
    let mut found_title = false;

    for line in content.lines() {
        if let Ok(obj) = serde_json::from_str::<serde_json::Value>(line) {
            let msg_type = obj.get("type").and_then(|v| v.as_str());

            if msg_type == Some("PLANNER_RESPONSE") && !found_title {
                if let Some(content_str) = obj.get("content").and_then(|v| v.as_str()) {
                    if let Some(start_idx) = content_str.find("<THREAD_NAME>") {
                        if let Some(end_idx) = content_str[start_idx..].find("</THREAD_NAME>") {
                            title = content_str[start_idx + 13..start_idx + end_idx]
                                .trim()
                                .to_string();
                            found_title = true;
                        }
                    }
                }
            }

            if msg_type == Some("USER_INPUT") && snippet.is_empty() {
                if let Some(prompt_content) =
                    obj.get("content").and_then(|v| v.as_str())
                {
                    let mut raw_prompt = prompt_content.to_string();
                    if let Some(start_idx) = raw_prompt.find("<USER_REQUEST>") {
                        if let Some(end_idx) = raw_prompt.find("</USER_REQUEST>") {
                            raw_prompt =
                                raw_prompt[start_idx + 14..end_idx].trim().to_string();
                        }
                    }

                    if let Some(sys_idx) = raw_prompt.find("<SYSTEM_INSTRUCTIONS>") {
                        raw_prompt = raw_prompt[..sys_idx].trim().to_string();
                    }

                    if raw_prompt.contains("Continuing conversation from history") {
                        if let Some(user_req_idx) = raw_prompt.find("\nUser request:") {
                            raw_prompt = raw_prompt
                                [user_req_idx + "\nUser request:".len()..]
                                .trim()
                                .to_string();
                        } else if let Some(user_req_idx) = raw_prompt.rfind("User request:") {
                            raw_prompt = raw_prompt
                                [user_req_idx + "User request:".len()..]
                                .trim()
                                .to_string();
                        }
                    }

                    let clean_prompt =
                        raw_prompt.replace("\r", "").replace("\n", " ");
                    let char_count = clean_prompt.chars().count();

                    if !found_title {
                        title = if char_count > 40 {
                            format!(
                                "{}...",
                                clean_prompt.chars().take(40).collect::<String>()
                            )
                        } else {
                            clean_prompt.clone()
                        };
                    }

                    snippet = if char_count > 120 {
                        format!(
                            "{}...",
                            clean_prompt.chars().take(30).collect::<String>()
                        )
                    } else {
                        clean_prompt
                    };
                }
            }

            if found_title && !snippet.is_empty() {
                break;
            }
        }
    }

    let parsed_timestamp =
        get_last_message_timestamp(latest_filepath).unwrap_or(mtime);

    let info = CachedThreadInfo {
        mtime,
        size,
        project_path,
        title,
        snippet,
        parsed_timestamp,
    };

    let mut cache = cache_mutex.lock().unwrap();
    cache.insert(latest_thread_id.to_string(), info.clone());
    Some(info)
}

// ---------------------------------------------------------------------------
// Project path detection
// ---------------------------------------------------------------------------

fn detect_project_path(content: &str) -> Option<String> {
    let home = std::env::var("HOME").unwrap_or_else(|_| "/Users/matt".to_string());
    let projects_prefix = format!("{}/projects/", home);

    // 1. Try to extract from tool calls arguments (most accurate)
    for line in content.lines() {
        if let Ok(obj) = serde_json::from_str::<serde_json::Value>(line) {
            if let Some(tool_calls) = obj.get("tool_calls").and_then(|v| v.as_array()) {
                for tc in tool_calls {
                    if let Some(args) = tc.get("args").and_then(|v| v.as_object()) {
                        for key in &[
                            "Cwd",
                            "AbsolutePath",
                            "SearchPath",
                            "TargetFile",
                            "DirectoryPath",
                        ] {
                            if let Some(val_str) = args.get(*key).and_then(|v| v.as_str()) {
                                let normalized = val_str.replace(
                                    "/Users/matthewmurphy/",
                                    &format!("{}/", home),
                                );
                                if normalized.starts_with(&projects_prefix) {
                                    let after = &normalized[projects_prefix.len()..];
                                    let end_pos =
                                        after.find('/').unwrap_or(after.len());
                                    let project_name = &after[..end_pos];
                                    if !project_name.is_empty() {
                                        return Some(format!(
                                            "{}{}",
                                            projects_prefix, project_name
                                        ));
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // 2. Fallback to scanning text
    let normalized_content = content.replace("/Users/matthewmurphy", &home);

    let mut search_content = &normalized_content[..];
    if let Some(user_req_start) = normalized_content.find("<USER_REQUEST>") {
        search_content = &normalized_content[user_req_start..];
    }

    if let Some(pos) = search_content.find(&projects_prefix) {
        let after_prefix = &search_content[pos + projects_prefix.len()..];
        let end_pos = after_prefix
            .find(|c: char| {
                c == '/'
                    || c == '"'
                    || c == '\''
                    || c == '\\'
                    || c == ','
                    || c == '`'
                    || c == '*'
                    || c == ')'
                    || c == ']'
                    || c == '}'
                    || c == ':'
                    || c == ';'
                    || c == '.'
                    || c.is_whitespace()
            })
            .unwrap_or(after_prefix.len());

        let mut project_name = &after_prefix[..end_pos];
        while !project_name.is_empty()
            && project_name.ends_with(|c: char| {
                c == '`'
                    || c == '*'
                    || c == '.'
                    || c == ','
                    || c == '`'
                    || c == ':'
                    || c == ';'
                    || c == ')'
                    || c == ']'
            })
        {
            project_name = &project_name[..project_name.len() - 1];
        }
        if !project_name.is_empty() {
            return Some(format!("{}{}", projects_prefix, project_name));
        }
    }
    None
}

// ---------------------------------------------------------------------------
// Thread commands
// ---------------------------------------------------------------------------

#[tauri::command]
pub async fn get_project_threads(project_path: String) -> Result<Vec<ThreadLog>, String> {
    let home = std::env::var("HOME").map_err(|_| "Could not find HOME directory".to_string())?;
    let brain_dir = std::path::Path::new(&home)
        .join(".gemini")
        .join("antigravity-cli")
        .join("brain");

    if !brain_dir.exists() {
        return Ok(Vec::new());
    }

    let is_misc =
        project_path.ends_with("/projects/Misc") || project_path == "Misc";

    let (child_to_parent, thread_mtimes) = scan_brain_threads(&brain_dir);

    let mut groups: HashMap<String, Vec<String>> = HashMap::new();
    for thread_id in thread_mtimes.keys() {
        let root_id = get_root_thread_id(thread_id, &child_to_parent);
        groups.entry(root_id).or_default().push(thread_id.clone());
    }

    let mut group_vec: Vec<(String, Vec<String>)> = groups.into_iter().collect();
    for (_root_id, members) in &mut group_vec {
        members.sort_by(|a, b| {
            thread_mtimes
                .get(a)
                .cloned()
                .unwrap_or(0)
                .cmp(&thread_mtimes.get(b).cloned().unwrap_or(0))
                .then_with(|| a.cmp(b))
        });
    }
    group_vec.sort_by(|a, b| {
        let mtime_a = thread_mtimes
            .get(a.1.last().unwrap())
            .cloned()
            .unwrap_or(0);
        let mtime_b = thread_mtimes
            .get(b.1.last().unwrap())
            .cloned()
            .unwrap_or(0);
        mtime_b
            .cmp(&mtime_a)
            .then_with(|| a.0.cmp(&b.0))
    });

    let mut thread_logs = Vec::new();

    for (root_id, members) in group_vec {
        let root_thread_id = &root_id;
        let latest_thread_id = members.last().unwrap();

        let root_dir = brain_dir.join(root_thread_id);
        let root_filepath = root_dir
            .join(".system_generated")
            .join("logs")
            .join("transcript.jsonl");

        let latest_dir = brain_dir.join(latest_thread_id);
        let latest_filepath = latest_dir
            .join(".system_generated")
            .join("logs")
            .join("transcript.jsonl");

        if !root_filepath.exists() || !latest_filepath.exists() {
            continue;
        }

        let info = match get_cached_thread_info(&latest_filepath, latest_thread_id) {
            Some(i) => i,
            None => continue,
        };

        let _root_info =
            match get_cached_thread_info(&root_filepath, root_thread_id) {
                Some(i) => i,
                None => continue,
            };

        let matched = if is_misc {
            info.project_path.is_none()
        } else {
            if let Some(ref p_path) = info.project_path {
                if let Some(pos) = p_path.find(&project_path) {
                    let after_match = &p_path[pos + project_path.len()..];
                    let is_exact = match after_match.chars().next() {
                        Some(c) => !c.is_alphanumeric() && c != '_' && c != '-',
                        None => true,
                    };
                    is_exact
                } else {
                    false
                }
            } else {
                false
            }
        };

        if matched {
            thread_logs.push(ThreadLog {
                id: root_id,
                latest_leaf_id: latest_thread_id.clone(),
                title: info.title,
                snippet: info.snippet,
                filepath: root_filepath.to_string_lossy().to_string(),
                mtime: info.parsed_timestamp,
                detected_project_path: Some(project_path.clone()),
            });
        }
    }

    thread_logs.sort_by(|a, b| b.mtime.cmp(&a.mtime).then_with(|| a.id.cmp(&b.id)));
    Ok(thread_logs)
}

#[tauri::command]
pub async fn get_all_agy_threads() -> Result<Vec<ThreadLog>, String> {
    let home = std::env::var("HOME").map_err(|_| "Could not find HOME directory".to_string())?;
    let brain_dir = std::path::Path::new(&home)
        .join(".gemini")
        .join("antigravity-cli")
        .join("brain");

    if !brain_dir.exists() {
        return Ok(Vec::new());
    }

    let (child_to_parent, thread_mtimes) = scan_brain_threads(&brain_dir);

    let mut groups: HashMap<String, Vec<String>> = HashMap::new();
    for thread_id in thread_mtimes.keys() {
        let root_id = get_root_thread_id(thread_id, &child_to_parent);
        groups.entry(root_id).or_default().push(thread_id.clone());
    }

    let mut group_vec: Vec<(String, Vec<String>)> = groups.into_iter().collect();
    for (_root_id, members) in &mut group_vec {
        members.sort_by(|a, b| {
            thread_mtimes
                .get(a)
                .cloned()
                .unwrap_or(0)
                .cmp(&thread_mtimes.get(b).cloned().unwrap_or(0))
                .then_with(|| a.cmp(b))
        });
    }
    group_vec.sort_by(|a, b| {
        let mtime_a = thread_mtimes
            .get(a.1.last().unwrap())
            .cloned()
            .unwrap_or(0);
        let mtime_b = thread_mtimes
            .get(b.1.last().unwrap())
            .cloned()
            .unwrap_or(0);
        mtime_b
            .cmp(&mtime_a)
            .then_with(|| a.0.cmp(&b.0))
    });

    let mut thread_logs = Vec::new();

    for (root_id, members) in group_vec {
        let root_thread_id = &root_id;
        let latest_thread_id = members.last().unwrap();

        let root_dir = brain_dir.join(root_thread_id);
        let root_filepath = root_dir
            .join(".system_generated")
            .join("logs")
            .join("transcript.jsonl");

        let latest_dir = brain_dir.join(latest_thread_id);
        let latest_filepath = latest_dir
            .join(".system_generated")
            .join("logs")
            .join("transcript.jsonl");

        if !root_filepath.exists() || !latest_filepath.exists() {
            continue;
        }

        let info = match get_cached_thread_info(&latest_filepath, latest_thread_id) {
            Some(i) => i,
            None => continue,
        };

        let _root_info =
            match get_cached_thread_info(&root_filepath, root_thread_id) {
                Some(i) => i,
                None => continue,
            };

        thread_logs.push(ThreadLog {
            id: root_id,
            latest_leaf_id: latest_thread_id.clone(),
            title: info.title,
            snippet: info.snippet,
            filepath: root_filepath.to_string_lossy().to_string(),
            mtime: info.parsed_timestamp,
            detected_project_path: info.project_path,
        });
    }

    thread_logs.sort_by(|a, b| b.mtime.cmp(&a.mtime).then_with(|| a.id.cmp(&b.id)));
    Ok(thread_logs)
}

#[tauri::command]
pub fn delete_thread(id: String) -> Result<(), String> {
    let home = std::env::var("HOME").map_err(|_| "Could not find HOME directory".to_string())?;
    let brain_dir = std::path::Path::new(&home)
        .join(".gemini")
        .join("antigravity-cli")
        .join("brain");

    if !brain_dir.exists() {
        return Ok(());
    }

    let (child_to_parent, thread_mtimes) = scan_brain_threads(&brain_dir);
    let root_id = get_root_thread_id(&id, &child_to_parent);

    for thread_id in thread_mtimes.keys() {
        if get_root_thread_id(thread_id, &child_to_parent) == root_id {
            let thread_dir = brain_dir.join(thread_id);
            if thread_dir.exists() {
                let _ = std::fs::remove_dir_all(&thread_dir);
            }
        }
    }

    let root_dir = brain_dir.join(&root_id);
    if root_dir.exists() {
        let _ = std::fs::remove_dir_all(&root_dir);
    }

    Ok(())
}

fn get_thread_id_from_path(filepath: &str) -> Option<String> {
    let path = std::path::Path::new(filepath);
    for ancestor in path.ancestors() {
        if let Some(parent) = ancestor.parent() {
            if parent.file_name()?.to_string_lossy() == "brain" {
                return Some(ancestor.file_name()?.to_string_lossy().to_string());
            }
        }
    }
    None
}

#[tauri::command]
pub async fn read_thread_log(filepath: String) -> Result<String, String> {
    let home = std::env::var("HOME").map_err(|_| "Could not find HOME directory".to_string())?;
    let brain_dir = std::path::Path::new(&home)
        .join(".gemini")
        .join("antigravity-cli")
        .join("brain");

    if let Some(thread_id) = get_thread_id_from_path(&filepath) {
        if brain_dir.exists() {
            let (child_to_parent, thread_mtimes) = scan_brain_threads(&brain_dir);
            let root_id = get_root_thread_id(&thread_id, &child_to_parent);
            let chain = get_thread_chain(&root_id, &child_to_parent, &thread_mtimes);

            if !chain.is_empty() {
                let mut combined_content = String::new();
                for id in chain {
                    let log_path = brain_dir
                        .join(id)
                        .join(".system_generated")
                        .join("logs")
                        .join("transcript.jsonl");
                    if log_path.exists() {
                        if let Ok(content) = std::fs::read_to_string(log_path) {
                            if !combined_content.is_empty()
                                && !combined_content.ends_with('\n')
                            {
                                combined_content.push('\n');
                            }
                            combined_content.push_str(&content);
                        }
                    }
                }
                return Ok(combined_content);
            }
        }
    }

    std::fs::read_to_string(filepath)
        .map_err(|e| format!("Failed to read thread log: {}", e))
}

#[tauri::command]
pub fn file_exists(filepath: String) -> bool {
    std::path::Path::new(&filepath).exists()
}

// ---------------------------------------------------------------------------
// Thread patch (Hermes integration)
// ---------------------------------------------------------------------------

#[tauri::command]
pub fn patch_thread_log_with_output(
    project_path: String,
    active_thread_id: Option<String>,
    output_content: String,
) -> Result<String, String> {
    let home = std::env::var("HOME").map_err(|_| "Could not find HOME directory".to_string())?;
    let brain_dir = std::path::Path::new(&home)
        .join(".gemini")
        .join("antigravity-cli")
        .join("brain");

    if !brain_dir.exists() {
        return Err("Brain directory does not exist".to_string());
    }

    let target_id = active_thread_id
        .filter(|id| !id.trim().is_empty())
        .unwrap_or_default();

    let target_thread_id = if !target_id.is_empty() {
        let (child_to_parent, thread_mtimes) = scan_brain_threads(&brain_dir);
        let root_id = get_root_thread_id(&target_id, &child_to_parent);
        let mut chain = get_thread_chain(&root_id, &child_to_parent, &thread_mtimes);
        chain.pop().unwrap_or(target_id)
    } else {
        let entries = std::fs::read_dir(&brain_dir)
            .map_err(|e| format!("Failed to read brain directory: {}", e))?;

        let mut latest_thread_id = None;
        let mut latest_mtime = 0;

        for entry in entries {
            if let Ok(entry) = entry {
                let path = entry.path();
                if path.is_dir() {
                    let thread_id =
                        path.file_name().unwrap().to_string_lossy().to_string();
                    let transcript_path = path
                        .join(".system_generated")
                        .join("logs")
                        .join("transcript.jsonl");

                    if transcript_path.exists() {
                        if let Ok(metadata) = std::fs::metadata(&transcript_path) {
                            let mtime = metadata
                                .modified()
                                .and_then(|t| {
                                    t.duration_since(std::time::UNIX_EPOCH)
                                        .map_err(|e| {
                                            std::io::Error::new(
                                                std::io::ErrorKind::Other,
                                                e,
                                            )
                                        })
                                })
                                .map(|d| d.as_secs())
                                .unwrap_or(0);

                            if mtime > latest_mtime {
                                use std::io::Read;
                                if let Ok(file) = std::fs::File::open(&transcript_path)
                                {
                                    let mut buffer = Vec::new();
                                    let _ = file.take(131072).read_to_end(&mut buffer);
                                    let content =
                                        String::from_utf8_lossy(&buffer);

                                    if let Some(pos) =
                                        content.find(&project_path)
                                    {
                                        let after_match = &content
                                            [pos + project_path.len()..];
                                        let is_exact =
                                            match after_match.chars().next() {
                                                Some(c) => {
                                                    !c.is_alphanumeric()
                                                        && c != '_'
                                                        && c != '-'
                                                }
                                                None => true,
                                            };
                                        if is_exact {
                                            latest_mtime = mtime;
                                            latest_thread_id =
                                                Some(thread_id);
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        match latest_thread_id {
            Some(id) => id,
            None => {
                return Err("No matching thread found for this project".to_string())
            }
        }
    };

    let thread_dir = brain_dir.join(&target_thread_id);
    let transcript_path = thread_dir
        .join(".system_generated")
        .join("logs")
        .join("transcript.jsonl");
    let transcript_full_path = thread_dir
        .join(".system_generated")
        .join("logs")
        .join("transcript_full.jsonl");

    let patch_file = |path: &std::path::Path| -> Result<(), String> {
        if !path.exists() {
            return Ok(());
        }
        let content = std::fs::read_to_string(path)
            .map_err(|e| format!("Failed to read transcript: {}", e))?;

        let mut lines: Vec<String> =
            content.lines().map(|s| s.to_string()).collect();
        let mut patched = false;

        for i in (0..lines.len()).rev() {
            if let Ok(mut obj) =
                serde_json::from_str::<serde_json::Value>(&lines[i])
            {
                if obj.get("source").and_then(|v| v.as_str()) == Some("MODEL")
                    && obj.get("type").and_then(|v| v.as_str())
                        == Some("PLANNER_RESPONSE")
                    && obj.get("content").is_some()
                {
                    obj["content"] =
                        serde_json::Value::String(output_content.clone());
                    if let Ok(new_line) = serde_json::to_string(&obj) {
                        lines[i] = new_line;
                        patched = true;
                        break;
                    }
                }
            }
        }

        if patched {
            let mut new_content = lines.join("\n");
            if !new_content.ends_with('\n') && !new_content.is_empty() {
                new_content.push('\n');
            }
            std::fs::write(path, new_content)
                .map_err(|e| format!("Failed to write patched transcript: {}", e))?;
        }
        Ok(())
    };

    patch_file(&transcript_path)?;
    patch_file(&transcript_full_path)?;

    Ok(target_thread_id)
}

// ---------------------------------------------------------------------------
// Thread search
// ---------------------------------------------------------------------------

fn extract_user_request(content: &str) -> String {
    if let Some(start) = content.find("<USER_REQUEST>") {
        if let Some(end) = content.find("</USER_REQUEST>") {
            return content[start + 14..end].trim().to_string();
        }
    }
    content.to_string()
}

fn truncate_preview(content: &str, query: &str) -> String {
    let lower = content.to_lowercase();
    if let Some(pos) = lower.find(query) {
        let start = pos.saturating_sub(30);
        let end = (pos + query.len() + 80).min(content.len());

        let mut start_idx = start;
        while start_idx > 0 && !content.is_char_boundary(start_idx) {
            start_idx -= 1;
        }

        let mut end_idx = end;
        while end_idx < content.len() && !content.is_char_boundary(end_idx) {
            end_idx += 1;
        }

        let mut prev = String::new();
        if start_idx > 0 {
            prev.push_str("...");
        }
        prev.push_str(&content[start_idx..end_idx]);
        if end_idx < content.len() {
            prev.push_str("...");
        }
        prev.replace('\n', " ")
    } else {
        content
            .chars()
            .take(100)
            .collect::<String>()
            .replace('\n', " ")
    }
}

fn highlight_query_text(text: &str, query: &str) -> String {
    let query_lower = query.to_lowercase();
    let text_lower = text.to_lowercase();
    let mut result = String::new();
    let mut last_idx = 0;

    for (start_idx, _) in text_lower.match_indices(&query_lower) {
        if start_idx < last_idx {
            continue;
        }
        result.push_str(&text[last_idx..start_idx]);
        result.push_str("<mark>");
        result.push_str(&text[start_idx..start_idx + query.len()]);
        result.push_str("</mark>");
        last_idx = start_idx + query.len();
    }
    result.push_str(&text[last_idx..]);
    result
}

#[tauri::command]
pub async fn search_project_threads(
    project_path: String,
    query: String,
) -> Result<Vec<ThreadSearchResult>, String> {
    let threads = get_project_threads(project_path).await?;
    let query_lower = query.to_lowercase();
    let mut results = Vec::new();

    let home = std::env::var("HOME").map_err(|_| "Could not find HOME".to_string())?;
    let brain_dir = std::path::Path::new(&home)
        .join(".gemini")
        .join("antigravity-cli")
        .join("brain");

    for thread in threads {
        let mut score: u64 = 0;
        let mut preview = String::new();
        let mut matches = Vec::new();

        if thread.title.to_lowercase().contains(&query_lower) {
            score += 100_000_000;
        }

        let latest_filepath = brain_dir
            .join(&thread.latest_leaf_id)
            .join(".system_generated")
            .join("logs")
            .join("transcript.jsonl");
        if let Ok(content) = std::fs::read_to_string(&latest_filepath) {
            for line in content.lines() {
                if let Ok(parsed) =
                    serde_json::from_str::<serde_json::Value>(line)
                {
                    let step_type =
                        parsed.get("type").and_then(|v| v.as_str()).unwrap_or("");
                    let content_str = parsed
                        .get("content")
                        .and_then(|v| v.as_str())
                        .unwrap_or("");

                    let text_to_scan = if step_type == "USER_INPUT" {
                        extract_user_request(content_str)
                    } else if step_type == "PLANNER_RESPONSE"
                        || step_type == "MODEL"
                    {
                        content_str.to_string()
                    } else {
                        String::new()
                    };

                    if !text_to_scan.is_empty() {
                        let text_to_scan_clean = text_to_scan
                            .replace("<THREAD_NAME>", "")
                            .replace("</THREAD_NAME>", "");
                        if text_to_scan_clean
                            .to_lowercase()
                            .contains(&query_lower)
                        {
                            if step_type == "USER_INPUT" {
                                score += 50_000_000;
                            } else {
                                score += 10_000_000;
                            }

                            if preview.is_empty() {
                                preview = truncate_preview(
                                    &text_to_scan_clean,
                                    &query_lower,
                                );
                            }

                            for text_line in text_to_scan_clean.lines() {
                                if text_line
                                    .to_lowercase()
                                    .contains(&query_lower)
                                {
                                    let highlighted = highlight_query_text(
                                        text_line.trim(),
                                        &query,
                                    );
                                    if !matches.contains(&highlighted)
                                        && matches.len() < 5
                                    {
                                        matches.push(highlighted);
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        if score > 0 {
            score += thread.mtime as u64;
            results.push(ThreadSearchResult {
                thread,
                score,
                preview: if preview.is_empty() {
                    "Matched in title".to_string()
                } else {
                    preview
                },
                matches,
            });
        }
    }

    results.sort_by(|a, b| b.score.cmp(&a.score));
    Ok(results)
}
