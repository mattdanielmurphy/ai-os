---
title: "Initialize AI-OS Monorepo Structure"
date: "2026-08-15"
conversation_id: "cc3281de-7aad-4f85-a349-f44667644f52"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 15, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 80px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

You are a leaf file editor. Please execute the following file creations and updates in /Users/matt/projects/ai-os:

1. Create `/Users/matt/projects/ai-os/Cargo.toml` with:
```toml

[workspace]
members = [
    "crates/aios-core",
    "apps/gemini-companion/src-tauri",
    "apps/aios-tui",
]
resolver = "2"
```

2. Update `/Users/matt/projects/ai-os/package.json` with:
```json

{
  "name": "ai-os",
  "version": "1.0.0",
  "private": true,
  "workspaces": [
    "apps/*",
    "services/*"
  ],
  "scripts": {
    "gather-context": "code2prompt --include \"*.md,*.py,*.sh,bin/*\" --exclude \"apps/*,agent-logs/*,gemini-history/*,tmp/*,.git/*,node_modules/*\" -O ./tmp/codebase.txt && ./bin/copy-file-ref ./tmp/codebase.txt && echo \"Codebase context gathered to ./tmp/codebase.txt and file reference copied to clipboard.\"",
    "audit": "python3 ./scripts/audit_transcripts.py"
  },
  "devDependencies": {
    "@rollup/rollup-darwin-x64": "^4.62.2"
  }
}
```

3. Create `/Users/matt/projects/ai-os/crates/aios-core/Cargo.toml` with:
```toml

[package]
name = "aios-core"
version = "0.1.0"
edition = "2021"
description = "Core headless session, PTY, and thread tracking library for AI-OS"

[dependencies]
portable-pty = "0.8"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
futures-util = "0.3"
```

4. Create `/Users/matt/projects/ai-os/crates/aios-core/src/lib.rs` with:
```rust

pub mod types;
pub mod threads;
pub mod session;
pub mod pty;
```

5. Create `/Users/matt/projects/ai-os/crates/aios-core/src/types.rs` with:
```rust

use std::sync::{Arc, Mutex};
use std::collections::HashMap;
use portable_pty::MasterPty;
use std::io::Write;

// Core data types without Tauri dependencies

#[allow(dead_code)]
pub struct ProjectSession {
    pub claude_writer: Option<Box<dyn Write + Send>>,
    pub claude_master: Option<Box<dyn MasterPty + Send>>,
    pub claude_pid: Option<u32>,
    pub agy_writer: Option<Box<dyn Write + Send>>,
    pub agy_master: Option<Box<dyn MasterPty + Send>>,
    pub agy_pid: Option<u32>,
    pub hermes_writer: Option<Box<dyn Write + Send>>,
    pub hermes_master: Option<Box<dyn MasterPty + Send>>,
    pub hermes_pid: Option<u32>,
    pub mini_writer: Box<dyn Write + Send>,
    pub mini_master: Box<dyn MasterPty + Send>,
    pub mini_pid: u32,
    pub project_path: String,
    pub thread_id: String,
    pub last_accessed: std::time::SystemTime,
}

#[derive(Clone, serde::Serialize, serde::Deserialize, Debug)]
pub struct Payload {
    pub data: String,
    pub project_path: String,
    pub terminal_type: String,
    pub thread_id: String,
}

#[derive(Clone, serde::Serialize, serde::Deserialize, Debug)]
pub struct SwitchResult {
    pub shell_pid: u32,
    pub is_new_session: bool,
    pub hermes_ws_port: u16,
}

#[derive(Clone, serde::Serialize, serde::Deserialize, Debug)]
pub struct PauseStatusPayload {
    pub project_path: String,
    pub status: String,
}

#[derive(Clone, serde::Serialize, serde::Deserialize, Debug)]
pub struct ThreadLog {
    pub id: String,
    pub latest_leaf_id: String,
    pub title: String,
    pub snippet: String,
    pub filepath: String,
    pub mtime: u64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub detected_project_path: Option<String>,
}

#[derive(Clone, serde::Serialize, serde::Deserialize, Debug)]
pub struct ThreadSearchResult {
    pub thread: ThreadLog,
    pub score: u64,
    pub preview: String,
    pub matches: Vec<String>,
}

#[derive(serde::Deserialize, serde::Serialize, Debug)]
pub struct CommitPayload {
    pub thread_uuid: String,
    pub target_filename: String,
    pub content: String,
}

#[derive(Clone, serde::Serialize, serde::Deserialize, Debug)]
pub struct RevisionEvent {
    pub thread_uuid: String,
    pub target_filename: String,
    pub commit_hash: String,
}

#[derive(serde::Deserialize, serde::Serialize, Debug)]
pub struct ContextSyncPayload {
    pub thread_id: String,
    pub content: String,
}

#[derive(serde::Deserialize, serde::Serialize, Debug)]
pub struct GeminiSyncPayload {
    pub url: String,
    pub body: String,
}

#[derive(Clone, Debug)]
pub struct CachedThreadInfo {
    pub mtime: u64,
    pub size: u64,
    pub project_path: Option<String>,
    pub title: String,
    pub snippet: String,
    pub parsed_timestamp: u64,
}
```

6. Create `/Users/matt/projects/ai-os/crates/aios-core/src/threads.rs` with:
```rust

use std::path::{Path, PathBuf};
use std::fs;
use crate::types::{ThreadLog, ThreadSearchResult, CachedThreadInfo};

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
```

7. Create `/Users/matt/projects/ai-os/crates/aios-core/src/pty.rs` with:
```rust

use std::path::PathBuf;

pub fn get_ai_os_home() -> PathBuf {
    std::env::var("AI_OS_HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|_| {
            let home = std::env::var("HOME").unwrap_or_else(|_| "/Users/matt".to_string());
            PathBuf::from(home).join("projects").join("ai-os")
        })
}
```

8. Create `/Users/matt/projects/ai-os/crates/aios-core/src/session.rs` with:
```rust

use std::sync::{Arc, Mutex};
use std::collections::HashMap;
use crate::types::ProjectSession;

pub type SessionMap = Arc<Mutex<HashMap<String, ProjectSession>>>;

pub fn create_session_map() -> SessionMap {
    Arc::new(Mutex::new(HashMap::new()))
}
```

9. Create `/Users/matt/projects/ai-os/apps/aios-tui/Cargo.toml` with:
```toml

[package]
name = "aios-tui"
version = "0.1.0"
edition = "2021"
description = "Headless Terminal UI harness for AI-OS"

[dependencies]
aios-core = { path = "../../crates/aios-core" }
tokio = { version = "1", features = ["full"] }
crossterm = "0.28"
ratatui = "0.29"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

10. Create `/Users/matt/projects/ai-os/apps/aios-tui/src/main.rs` with:
```rust

use std::io;
use crossterm::{
    event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
    backend::CrosstermBackend,
    layout::{Constraint, Direction, Layout},
    style::{Color, Modifier, Style},
    text::{Line, Span},
    widgets::{Block, Borders, Paragraph},
    Terminal,
};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let home = aios_core::pty::get_ai_os_home();
    println!("Starting AI-OS TUI (Home: {})...", home.display());

    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen, EnableMouseCapture)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    let mut running = true;
    while running {
        terminal.draw(|f| {
            let chunks = Layout::default()
                .direction(Direction::Vertical)
                .constraints([
                    Constraint::Length(3),
                    Constraint::Min(1),
                    Constraint::Length(3),
                ])
                .split(f.area());

            let header = Paragraph::new(Line::from(vec![
                Span::styled("AI-OS ", Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD)),
                Span::styled("Terminal Harness (Headless Mode)", Style::default().fg(Color::White)),
            ]))
            .block(Block::default().borders(Borders::ALL).title(" AI-OS TUI "));
            f.render_widget(header, chunks[0]);

            let body = Paragraph::new(vec![
                Line::from("Connected to aios-core backend."),
                Line::from("Press 'q' or 'Esc' to exit to shell."),
            ])
            .block(Block::default().borders(Borders::ALL).title(" Status "));
            f.render_widget(body, chunks[1]);

            let footer = Paragraph::new("Press 'q' to quit | 'r' to refresh")
                .style(Style::default().fg(Color::DarkGray))
                .block(Block::default().borders(Borders::ALL));
            f.render_widget(footer, chunks[2]);
        })?;

        if event::poll(std::time::Duration::from_millis(100))? {
            if let Event::Key(key) = event::read()? {
                if matches!(key.code, KeyCode::Char('q') | KeyCode::Esc) {
                    running = false;
                }
            }
        }
    }

    disable_raw_mode()?;
    execute!(
        terminal.backend_mut(),
        LeaveAlternateScreen,
        DisableMouseCapture
    )?;
    terminal.show_cursor()?;

    println!("AI-OS TUI exited cleanly.");
    Ok(())
}
```

11. Update `/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/Cargo.toml` to add the aios-core dependency:
```toml

[package]
name = "tauri-app"
version = "0.1.0"
description = "A Tauri App"
authors = ["you"]
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[build-dependencies]
tauri-build = { version = "1", features = [] }

[dependencies]
aios-core = { path = "../../../crates/aios-core" }
tauri = { version = "1", features = [ "macos-private-api", "window-all", "global-shortcut-all", "fs-read-file", "fs-exists", "shell-open", "dialog", "devtools", "global-shortcut"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
portable-pty = "0.8"
tokio = { version = "1", features = ["full"] }
axum = { version = "0.8.9", features = ["ws"] }
tower-http = { version = "0.7.0", features = ["cors"] }
futures-util = "0.3"

[features]
# This feature is used for production builds or when a dev server is not specified, DO NOT REMOVE!!
custom-protocol = ["tauri/custom-protocol"]
```

12. Update `/Users/matt/projects/ai-os/bin/ai-os` to update the GUI launch path and add `--tui`:
Replace:
```bash

show_help() {
    echo "AI-OS CLI - Command Line Interface for Personal AI OS"
    echo ""
    echo "Usage:"
    echo "  ai-os [options] [arguments]"
    echo ""
    echo "Options:"
    echo "  --gui           Launch the Tauri GUI dashboard (default)"
    echo "  --cli           Run the Agy orchestrator agent in the current terminal"
    echo "  --terminal      Run the Agy orchestrator agent in the current terminal"
    echo "  --no-gui        Run the Agy orchestrator agent in the current terminal"
    echo "  --agy           Run the Agy orchestrator agent in the current terminal"
    echo "  --claude        Run the native Claude Code agent in the current terminal"
    echo "  --handover      Compile thread context and spawn a fresh thread with process replacement"
    echo "  wiki | --wiki   Launch Quartz Wiki web server at http://localhost:3333"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "All other arguments and flags are forwarded to the selected agent."
    exit 0
}
```

with:
```bash

show_help() {
    echo "AI-OS CLI - Command Line Interface for Personal AI OS"
    echo ""
    echo "Usage:"
    echo "  ai-os [options] [arguments]"
    echo ""
    echo "Options:"
    echo "  --gui           Launch the Tauri GUI dashboard (default)"
    echo "  --tui           Launch the headless AI-OS Terminal UI"
    echo "  --cli           Run the Agy orchestrator agent in the current terminal"
    echo "  --terminal      Run the Agy orchestrator agent in the current terminal"
    echo "  --no-gui        Run the Agy orchestrator agent in the current terminal"
    echo "  --agy           Run the Agy orchestrator agent in the current terminal"
    echo "  --claude        Run the native Claude Code agent in the current terminal"
    echo "  --handover      Compile thread context and spawn a fresh thread with process replacement"
    echo "  wiki | --wiki   Launch Quartz Wiki web server at http://localhost:3333"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "All other arguments and flags are forwarded to the selected agent."
    exit 0
}
```

And add case for `--tui`:
```bash

        --tui)
            echo "[ai-os] Launching AI-OS TUI in terminal..."
            cd "$AI_OS_HOME/apps/aios-tui" && cargo run --release
            exit 0
            ;;
```

And update the GUI launch block:
```bash

if [ "$LAUNCH_GUI" = true ]; then
    echo "[ai-os] Launching GUI interface..."
    export AIOS_INITIAL_PROJECT="$ORIGINAL_PWD"
    cd "$AI_OS_HOME/apps/gemini-companion" && bun run tauri dev
```

13. Update `/Users/matt/projects/ai-os/.gitignore` to add:
```gitignore

/apps/*/dist
/apps/*/node_modules
/apps/**/target
/crates/**/target
target/
```

14. Update `/Users/matt/projects/ai-os/AG_CONTEXT.md`:
Under `## Core Directories & Structure`, update to reflect:
- `/apps`: Monorepo applications:
  - `/apps/gemini-companion`: Dedicated Tauri shell for Gemini/Perplexity webview automation + IPC loopback daemon.
  - `/apps/aios-tui`: Headless terminal UI harness (Ratatui/Crossterm).
- `/crates`: Shared Rust libraries:
  - `/crates/aios-core`: Headless PTY, session, and thread tracking library.
- `/services`: Background daemons (`agy-proxy`, `clinical-trials`, etc.).
- `/tools`: Standalone helper tools.
- `/bin`: Wrapper scripts and orchestrator binaries (`ai-os`, `ai-os-wiki`, `triage`).

15. Append to `/Users/matt/projects/ai-os/DEVELOPMENT_JOURNAL.md`:
```markdown

## 2026-08-15
- **Stage 1 Monorepo Restructuring & Severing:** Restructured `ai-os` repository into an `apps/` and `crates/` monorepo layout. Moved `tauri-gui` to `apps/gemini-companion` preserving git history, extracted headless PTY/session/thread primitives into `crates/aios-core`, and created `apps/aios-tui` for terminal-based workflow orchestration. Updated root Cargo and Bun workspace configs, cleaned up stale lockfiles, and updated launcher entry points in `bin/ai-os`.
```

Perform all these file operations now.

</span>



<span title="Responded at 8:15am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The monorepo restructuring for `ai-os` is complete.

1.  **Workspace setup:** Root `Cargo.toml` and updated `package.json` with workspace configuration.
2.  **Library creation:** Extracted headless core primitives to [`crates/aios-core`](file:///Users/matt/projects/ai-os/crates/aios-core) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/crates/aios-core) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/crates/aios-core).
3.  **Application setup:** Created [`apps/aios-tui`](file:///Users/matt/projects/ai-os/apps/aios-tui) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/apps/aios-tui) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/apps/aios-tui) and integrated `aios-core` into both `apps/aios-tui` and [`apps/gemini-companion`](file:///Users/matt/projects/ai-os/apps/gemini-companion) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/apps/gemini-companion) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/apps/gemini-companion).
4.  **Tooling updates:** Updated [`bin/ai-os`](file:///Users/matt/projects/ai-os/bin/ai-os) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/bin/ai-os) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/bin/ai-os) to include the `--tui` launch flag and fixed the GUI launch path.
5.  **Documentation:** Updated [`.gitignore`](file:///Users/matt/projects/ai-os/.gitignore) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.gitignore) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.gitignore), [`AG_CONTEXT.md`](file:///Users/matt/projects/ai-os/AG_CONTEXT.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/AG_CONTEXT.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/AG_CONTEXT.md), and appended to [`DEVELOPMENT_JOURNAL.md`](file:///Users/matt/projects/ai-os/DEVELOPMENT_JOURNAL.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/DEVELOPMENT_JOURNAL.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/DEVELOPMENT_JOURNAL.md).

All requested file operations have been successfully applied.

</span>



</span>

</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">



**Thread Metrics:**

| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~43k | 3:15am | ~43k / ~403k 🟢 (optimal) | 108, 20 🔬, 16 📤 |

</span>