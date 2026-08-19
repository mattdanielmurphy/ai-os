---
title: "Configure Quartz Wiki Integration"
date: "2026-08-05"
conversation_id: "fd7f4682-03c9-4a12-ac5c-e32b4b74e575"
source: "antigravity"
---

# Configure Quartz Wiki Integration

## User

Please make the following file edits:

1. Create a executable bash script at `/Users/matt/projects/ai-os/bin/ai-os-wiki` with content:
```bash
#!/usr/bin/env bash
export AI_OS_HOME="/Users/matt/projects/ai-os"
echo "[ai-os wiki] Starting Quartz Wiki web server on http://localhost:3333..."
cd "$AI_OS_HOME/wiki-engine" || exit 1
exec npx tsx quartz/bootstrap-cli.mjs build --serve --port 3333
```
Make sure `ai-os-wiki` is saved.

2. Modify `/Users/matt/projects/ai-os/bin/ai-os`:
Add a case match for `wiki|--wiki)` in the option parsing loop (around line 63):
```bash
        wiki|--wiki)
            exec "$AI_OS_HOME/bin/ai-os-wiki"
            ;;
```
And add `wiki | --wiki  Launch Quartz Wiki web server at http://localhost:3333` in `show_help()`.

3. Update `/Users/matt/projects/ai-os/AG_CONTEXT.md`:
Append a bullet point under Key Architecture & Domain Rules:
`- **Documentation & Wiki Architecture (6 Boundaries + Quartz Wiki):** Documentation is partitioned into 6 distinct boundaries: (1) AI-OS Core Project Docs (\`~/projects/ai-os/docs/\`), (2) Me & Personal (\`Obsidian/Personal/\`), (3) Mac System Specs (\`Obsidian/Mac/\`), (4) Personal Notes & Ideas (\`Obsidian/Ideas/\`), (5) Project Conceptual Specs (\`Obsidian/Projects/<Name>/\`), and (6) Implementation Code Docs (\`~/projects/<Name>/docs/\`). The unified off-the-shelf **Quartz 4.0 Wiki Engine** aggregates these boundaries and is served locally on \`http://localhost:3333\` via \`ai-os wiki\` or \`ai-os-wiki\`.`

---

## Assistant

Created At: 2026-08-05T01:31:32-06:00
Completed At: 2026-08-05T01:31:32-06:00

				The command exited with code 1.
				Output:
				chmod: /Users/matt/projects/ai-os/bin/ai-os-wiki: No such file or directory

Created At: 2026-08-05T01:31:33-06:00
Completed At: 2026-08-05T01:31:33-06:00
Created file file:///Users/matt/projects/ai-os/bin/ai-os-wiki with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T01:31:34-06:00
Completed At: 2026-08-05T01:31:34-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-05T01:31:35-06:00
Completed At: 2026-08-05T01:31:35-06:00
File Path: `file:///Users/matt/projects/ai-os/bin/ai-os`
Total Lines: 112
Total Bytes: 3898
Showing lines 1 to 112
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: #!/usr/bin/env bash
2: 
3: export AI_OS_HOME="/Users/matt/projects/ai-os"
4: 
5: echo "[ai-os] Enforcing absolute context guardrails in ~/"
6: ln -sf "$AI_OS_HOME/CLAUDE.md" ~/CLAUDE.md
7: ln -sf "$AI_OS_HOME/docs/MEMORY.md" ~/MEMORY.md
8: export ZDOTDIR="$AI_OS_HOME"
9: ln -sfn "$AI_OS_HOME/docs/memory" ~/memory
10: 
11: # PHASE 4: macOS Profiling
12: # Generate a static state document of the environment on boot
13: PROFILE_PATH="$AI_OS_HOME/docs/memory/macOS_profile.md"
14: echo "[ai-os] Generating macOS system profile..."
15: echo "# macOS System Profile (Auto-Generated)" > "$PROFILE_PATH"
16: echo "## Storage & Volumes" >> "$PROFILE_PATH"
17: system_profiler SPStorageDataType >> "$PROFILE_PATH" 2>/dev/null
18: echo "## Active LaunchAgents" >> "$PROFILE_PATH"
19: ls -la ~/Library/LaunchAgents >> "$PROFILE_PATH" 2>/dev/null
20: echo "## Connected Displays" >> "$PROFILE_PATH"
21: system_profiler SPDisplaysDataType >> "$PROFILE_PATH" 2>/dev/null
22: echo "## Hammerspoon Config" >> "$PROFILE_PATH"
23: [ -f ~/.hammerspoon/init.lua ] && cat ~/.hammerspoon/init.lua | head -n 50 >> "$PROFILE_PATH" 2>/dev/null
24: 
25: # Generate the Stable Anchor Repo Map
26: echo "[ai-os] Updating Stable Anchor Repo Map..."
27: python3 "$AI_OS_HOME/scripts/generate_repo_map.py" "$AI_OS_HOME"
28: 
29: # Oneshot Hermes thread sync
30: echo "[ai-os] Running oneshot thread sync..."
31: python3 "$AI_OS_HOME/scripts/sync_threads.py" --oneshot
32: 
33: ORIGINAL_PWD="$PWD"
34: cd "$AI_OS_HOME" || exit
35: 
36: # Argument parsing
37: ENGINE="agy"
38: LAUNCH_GUI=true
39: 
40: show_help() {
41:     echo "AI-OS CLI 
<truncated 772 bytes>
cess replacement"
54:     echo "  -h, --help      Show this help message"
55:     echo ""
56:     echo "All other arguments and flags are forwarded to the selected agent."
57:     exit 0
58: }
59: 
60: # Parse options
61: while [[ $# -gt 0 ]]; do
62:     case "$1" in
63:         -h|--help)
64:             show_help
65:             ;;
66:         --gui)
67:             LAUNCH_GUI=true
68:             shift
69:             ;;
70:         --claude)
71:             ENGINE="claude"
72:             LAUNCH_GUI=false
73:             shift
74:             ;;
75:         --agy)
76:             ENGINE="agy"
77:             LAUNCH_GUI=false
78:             shift
79:             ;;
80:         --handover)
81:             exec python3 "$AI_OS_HOME/scripts/handover.py"
82:             ;;
83:         --cli|--no-gui|--terminal)
84:             LAUNCH_GUI=false
85:             shift
86:             ;;
87:         *)
88:             # Forward everything else to agent (only applicable if running non-GUI)
89:             break
90:             ;;
91:     esac
92: done
93: 
94: # Spawn background Hermes thread watcher
95: echo "[ai-os] Starting background thread sync watcher..."
96: python3 "$AI_OS_HOME/scripts/sync_threads.py" --watch &
97: SYNC_PID=$!
98: trap 'kill $SYNC_PID 2>/dev/null' EXIT
99: 
100: if [ "$LAUNCH_GUI" = true ]; then
101:     echo "[ai-os] Launching GUI interface..."
102:     export AIOS_INITIAL_PROJECT="$ORIGINAL_PWD"
103:     cd tauri-gui && bun run tauri dev
104: elif [ "$ENGINE" = "claude" ]; then
105:     echo "[ai-os] Launching Claude Code agent in terminal at $ORIGINAL_PWD..."
106:     cd "$ORIGINAL_PWD" || exit
107:     exec claude "$@" --dangerously-skip-permissions
108: else
109:     echo "[ai-os] Launching Agy orchestrator agent with Multi-Tier Triage in terminal at $ORIGINAL_PWD..."
110:     cd "$ORIGINAL_PWD" || exit
111:     exec python3 "$AI_OS_HOME/scripts/triage_router.py" "$@" --dangerously-skip-permissions
112: fi
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-05T01:31:36-06:00
Completed At: 2026-08-05T01:31:40-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/ai-os/bin/ai-os. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -51,6 +51,7 @@
     echo "  --agy           Run the Agy orchestrator agent in the current terminal"
     echo "  --claude        Run the native Claude Code agent in the current terminal"
     echo "  --handover      Compile thread context and spawn a fresh thread with process replacement"
+    echo "  wiki | --wiki   Launch Quartz Wiki web server at http://localhost:3333"
     echo "  -h, --help      Show this help message"
     echo ""
     echo "All other arguments and flags are forwarded to the selected agent."
@@ -83,6 +83,9 @@
             LAUNCH_GUI=false
             shift
             ;;
+        wiki|--wiki)
+            exec "$AI_OS_HOME/bin/ai-os-wiki"
+            ;;
         *)
             # Forward everything else to agent (only applicable if running non-GUI)
             break
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

We did our best to apply changes despite some inaccuracies. Double check if the edit applied is what you intended.

Created At: 2026-08-05T01:31:43-06:00
Completed At: 2026-08-05T01:31:43-06:00
File Path: `file:///Users/matt/projects/ai-os/AG_CONTEXT.md`
Total Lines: 29
Total Bytes: 3489
Showing lines 1 to 29
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Repository Context & Domain Knowledge
2: 
3: ## Project Overview
4: `ai-os` is a local-first AI harness designed to transform a macOS machine into an editable, interactive database of thoughts, files, and automation.
5: 
6: ## Core Directories & Structure
7: - `/bin`: Wrapper scripts and orchestrator binaries (e.g. `ai-os`, `agy`).
8: - `/docs`: Architecture, vision, memory, and strategy documentation.
9: - `/scripts`: Tool helper scripts (`subagent.py`, `get_last_cost.py`, `context_handoff.py`, `precision_edit.py`, `get-active-task.sh`, etc.).
10: - `/agent-logs`: Session engineering logs tracking goals, changes, and architecture discoveries (for agents).
11: - `/DEVELOPMENT_JOURNAL.md`: Human-readable timeline of key decisions and pivots (for the user).
12: - `/.devtool/features`: Features and user task specifications.
13: 
14: ## Key Architecture & Domain Rules
15: - **AI Clipboard Memory Tool (Usage: search-clipboard '<query>' [--pro])**: Agents can search macOS Alfred clipboard history using natural language by running ⚡ Flash model found no confident match. Auto-escalating to Gemini 2.5 Pro...
16: 
17: === AI Search Results for '<query>' ===
18: No matching items found by AI. non-interactively in terminal. Supports URL pre-filtering, brand alias expansion (e.g. g.co, gemini.google.com), and auto-escalation to Gemini 2.5 Pro.
19: - **Stable Anchor + Volatile Append Context Strategy:** Uses a structural map (repo map generated via AST parser/tree-sitter) as the stable front of the prompt context, and appends only active files and user requests at the end to maximize cache h
<truncated 20 bytes>
ion Philosophy:** agy handles work directly by default, using its native tools. When delegation makes sense (large context savings), agy prefers self-delegation (`agy -p`) over external tools like Claude Code to avoid per-call costs. Extreme delegation mode (always delegate to Claude Code) is preserved as a skill for when it's needed.
21: - **Dual-Rail Google Grid:** Seamlessly rotates Google accounts/authentication to double task quotas and VM limits.
22: - **Context Sync Protocol:** Userscript (`gemini.js`) integrated into browser/Tauri webview connects live Google web interface turns back to the Rust loopback daemon (`/api/context/sync`, `/api/notes/save`, `/api/revision/commit`) to serialize and version active text revisions in Git.
23: - **Three-Turn Delegation Protocol (Extreme Mode Only):** Available as the `agy-extreme-delegation` skill. Not the default — agy handles work directly with pragmatic self-delegation.
24: - **Hermes Thread Sync Daemon:** Integrates and synchronizes CLI/GUI NDJSON execution logs (`~/.gemini/antigravity-cli/brain/`) with Hermes' FTS5-enabled SQLite database (`~/.hermes/state.db`) bidirectionally. It launches as a background subprocess via the `bin/ai-os` execution wrapper, maintaining a unified search history across both platforms.
25: - **Hermes System Prompt Handoff**: Enabled the `agymcp` server to dynamically extract the active Hermes system prompt from `~/.hermes/state.db` and prepend it to prompts sent to `agy` (via `agy`, `agy_continue`, and `agy_start`) to align instructions and preserve behavioral consistency during task handoffs.
26: - **Multi-Tier Triage Routing & Pre-Flight Quota Check**: Evaluates remaining quota using `ag-quota -j` (or `codexbar status`). Automatically switches Antigravity to Minimal-Token Mode (Strict Orchestrator Mode 3) if remaining quota is low (<25%) or burning quickly, delegating code generation to `claude code` or cheap LiteLLM/subagent models.
27: 
28: 
29: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-05T01:31:45-06:00
Completed At: 2026-08-05T01:31:45-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/ai-os/AG_CONTEXT.md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -24,6 +24,7 @@
 - **Hermes Thread Sync Daemon:** Integrates and synchronizes CLI/GUI NDJSON execution logs (`~/.gemini/antigravity-cli/brain/`) with Hermes' FTS5-enabled SQLite database (`~/.hermes/state.db`) bidirectionally. It launches as a background subprocess via the `bin/ai-os` execution wrapper, maintaining a unified search history across both platforms.
 - **Hermes System Prompt Handoff**: Enabled the `agymcp` server to dynamically extract the active Hermes system prompt from `~/.hermes/state.db` and prepend it to prompts sent to `agy` (via `agy`, `agy_continue`, and `agy_start`) to align instructions and preserve behavioral consistency during task handoffs.
 - **Multi-Tier Triage Routing & Pre-Flight Quota Check**: Evaluates remaining quota using `ag-quota -j` (or `codexbar status`). Automatically switches Antigravity to Minimal-Token Mode (Strict Orchestrator Mode 3) if remaining quota is low (<25%) or burning quickly, delegating code generation to `claude code` or cheap LiteLLM/subagent models.
+- **Documentation & Wiki Architecture (6 Boundaries + Quartz Wiki):** Documentation is partitioned into 6 distinct boundaries: (1) AI-OS Core Project Docs (`~/projects/ai-os/docs/`), (2) Me & Personal (`Obsidian/Personal/`), (3) Mac System Specs (`Obsidian/Mac/`), (4) Personal Notes & Ideas (`Obsidian/Ideas/`), (5) Project Conceptual Specs (`Obsidian/Projects/<Name>/`), and (6) Implementation Code Docs (`~/projects/<Name>/docs/`). The unified off-the-shelf **Quartz 4.0 Wiki Engine** aggregates these boundaries and is served locally on `http://localhost:3333` via `ai-os wiki` or `ai-os-wiki`.
 
 
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-05T01:31:46-06:00
Completed At: 2026-08-05T01:31:46-06:00
Message sent to "fd282fc4-76da-473a-95ac-f18bc6ccd868".

All requested edits are complete:

1.  Created the executable bash script [`ai-os-wiki`](file:///Users/matt/projects/ai-os/bin/ai-os-wiki).
2.  Modified [`ai-os`](file:///Users/matt/projects/ai-os/bin/ai-os) to support the new `wiki|--wiki` command and updated the help menu.
3.  Updated [`AG_CONTEXT.md`](file:///Users/matt/projects/ai-os/AG_CONTEXT.md) to include the new architecture rules.

---
