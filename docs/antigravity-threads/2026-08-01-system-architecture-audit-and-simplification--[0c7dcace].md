---
title: "System Architecture Audit And Simplification"
date: "2026-08-01"
conversation_id: "0c7dcace-44ab-416e-9f00-937aa3daf9e7"
source: "antigravity"
---

# System Architecture Audit And Simplification

## User

[HERMES_SYSTEM_PROMPT]
You are Hermes Agent, the primary high-level reasoning engine for Matt's local AI orchestration system. You operate as the daily-driver architect and executor alongside `agy` (a separate, cheaper worker-bee CLI that lives in `~/projects/ai-os`). You and agy are parallel systems — you do not share context files, but you may call agy's scripts as subagents when beneficial.

## Who You Work For

Matt is a CS student and drummer. He self-studies calculus, tends to procrastinate, and responds best to atomic, immediately-actionable tasks.

### Active Projects
- **ai-os** (`~/projects/ai-os`) — Local-first AI harness (Tauri + Rust + Gemini integration)
- **CockBand** — Drum/bass Rocksmith-style clone
- **StudyEngine** — PencilKit/LaTeX note-taking app
- **Piano OS** — Tauri/Rust MIDI platform

## Absolute Knowledge Routing

These routing rules are non-negotiable and override any other memory or context:

- **"Notes", "personal notes", "my notes", "saved notes"** → Route EXCLUSIVELY to the iCloud Obsidian vault at:
  `/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/`
  Use the Obsidian skill (load with `skill_view(name='obsidian')`) for reading/writing vault content. When creating notes, use human-readable filenames (e.g., `Space Facts 🚀.md`) and provide clickable `file://` links.

- **Session engineering logs** → Write to the relevant project's `agent-logs/` directory. For ai-os specifically: `/Users/matt/projects/ai-os/agent-logs/`

## Hard Constraints

1. **Package manager:** `pnpm` exclusively. Never use `npm` or `yarn`.
2. **Safety:** Never use `rm`. Use `mv [path] ~/.Trash/` instead.
3. **Privacy:** All generated GitHub repos must use `--private`.
4. **No repo in ~:** Never initialize a git repository in the home directory.
5. **Local temp:** Use `./tmp` within the project directory, never `/tmp`.
6. **Username guardrail:** The host migrated from `matthewmurphy` to `matt`. Translate any `/Users/matthewmurphy/` paths to `/Users/matt/`.
<truncated 65843 bytes>
ds replacing, leave everything else untouched. Default to precision-scoping in any migration or refactoring.
§
Delegate: use delegate_task for multi-step/execution-heavy work instead of handling directly in the main thread. Cheap subagents preferred.
§
Direct correction style: when a feature doesn't work, the user says exactly what's wrong and expects the fix immediately, not a diagnostic back-and-forth. Anticipate edge cases (browser-level shortcuts, platform quirks) BEFORE implementing, not after the failure.

Conversation started: Tuesday, July 28, 2026
Model: deepseek/deepseek-v4-flash
Provider: openrouter
[/HERMES_SYSTEM_PROMPT]

[USER_PROMPT]
You are the primary system architect running on Gemini 3.1 Pro (High).
The user is feeling frustrated and overwhelmed because system rules, prompt injections, and subagent delegation have become complex, leaky, and unpredictable.

YOUR TASK:
1. Conduct a full, calm, ground-up audit of our prompt assembly and rule system in /Users/matt/projects/ai-os.
2. Review /Users/matt/projects/ai-os/scripts/compile_dynamic_prompt.py, /Users/matt/projects/ai-os/scripts/preflight.py, and all files in /Users/matt/projects/ai-os/.rules/.
3. Formulate a simple, rock-solid, non-fragile architecture to ensure:
   - Rules are clean, minimal, and non-conflicting.
   - Subagents spawned via agymcp or invoke_subagent get strictly relevant leaf instructions without context bloat or unwanted protocol overrides.
   - Main thread agents get clear, reliable instructions without breaking or getting stuck in loops.
4. Output a concise, reassuring, step-by-step master simplification plan.
[/USER_PROMPT]

---

## Assistant

Created At: 2026-07-31T21:48:32-06:00
Completed At: 2026-07-31T21:48:32-06:00
{"name":"agent_logs.md","sizeBytes":"709"}
{"name":"claude_only.md","sizeBytes":"1654"}
{"name":"common.md","sizeBytes":"29103"}
{"name":"core_safety.md","sizeBytes":"2433"}
{"name":"gemini_only.md","sizeBytes":"7892"}
{"name":"git_protocol.md","sizeBytes":"659"}
{"name":"hermes_only.md","sizeBytes":"1197"}
{"name":"mac_env.md","sizeBytes":"552"}
{"name":"subagent_leaf.md","sizeBytes":"556"}

Summary: This directory contains 0 subdirectories and 9 files.

Created At: 2026-07-31T21:48:32-06:00
Completed At: 2026-07-31T21:48:32-06:00
File Path: `file:///Users/matt/projects/ai-os/scripts/compile_dynamic_prompt.py`
Total Lines: 72
Total Bytes: 2496
Showing lines 1 to 72
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: #!/usr/bin/env python3
2: """
3: compile_dynamic_prompt.py - Dynamic System Prompt Compiler for ai-os
4: 
5: Assembles a minimal, tailored system prompt based on role (orchestrator vs leaf)
6: and task context/keywords.
7: """
8: 
9: import os
10: import sys
11: import argparse
12: from pathlib import Path
13: 
14: RULES_DIR = Path("/Users/matt/projects/ai-os/.rules")
15: 
16: def read_rule(name: str) -> str:
17:     path = RULES_DIR / f"{name}.md"
18:     if path.exists():
19:         with open(path, "r", encoding="utf-8") as f:
20:             return f.read().strip()
21:     return ""
22: 
23: def compile_stub(platform: str = "antigravity") -> str:
24:     return """# Antigravity Dynamic Context Stub
25: Run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` at session start to retrieve your full system directive if not already provided.
26: """
27: 
28: def compile_prompt(role: str = "orchestrator", platform: str = "antigravity", prompt_text: str = "", stub: bool = False) -> str:
29:     if stub and role.lower() != "leaf":
30:         return compile_stub(platform)
31: 
32:     sections = []
33:     
34:     # Always include core safety
35:     sections.append(read_rule("core_safety"))
36: 
37:     if role.lower() == "leaf":
38:         sections.append(read_rule("subagent_leaf"))
39:         return "\n\n".join(sections)
40: 
41:     # Orchestrator mode: add protocols
42:     sections.append(read_rule("git_protocol"))
43:     sections.append(read_rule("agent_logs"))
44: 
45:     # Platform specific rules
46:     if platform.lower() == "antigravity":
47:         sections.append(read_rule("gemini_only"))
48:     elif platform.lower() == "claude":
49:         sections.append(read_rule("claude_only"))
50:     elif platform.lower() == "hermes":
51:         sections.append(read_rule("hermes_only"))
52: 
53:     # Dynamic context based on prompt keywords
54:     p_lower = prompt_text.lower()
55:     if any(kw in p_lower for kw in ["mac", "hammerspoon", "tcc", "shortcut", "launchagent"]):
56:         sections.append(read_rule("mac_env"))
57: 
58:     return "\n\n".join(sections)
59: 
60: def main():
61:     parser = argparse.ArgumentParser(description="Dynamic System Prompt Compiler")
62:     parser.add_argument("--role", default="orchestrator", choices=["orchestrator", "leaf"], help="Agent role")
63:     parser.add_argument("--platform", default="antigravity", choices=["antigravity", "claude", "hermes", "agy"], help="Target platform")
64:     parser.add_argument("--prompt", default="", help="User prompt string for keyword matching")
65: 
66:     args = parser.parse_args()
67:     compiled = compile_prompt(args.role, args.platform, args.prompt)
68:     print(compiled)
69: 
70: if __name__ == "__main__":
71:     main()
72: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T21:48:32-06:00
Completed At: 2026-07-31T21:48:32-06:00
File Path: `file:///Users/matt/projects/ai-os/scripts/preflight.py`
Total Lines: 144
Total Bytes: 5860
Showing lines 1 to 144
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import subprocess
2: import sys
3: import os
4: import datetime
5: import concurrent.futures
6: import json
7: 
8: sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
9: 
10: def run_cmd(args, check=False):
11:     try:
12:         res = subprocess.run(args, capture_output=True, text=True, check=check)
13:         return res.stdout.strip(), res.returncode
14:     except Exception as e:
15:         return "", 1
16: 
17: def log_preflight(status):
18:     ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
19:     log_msg = f"{ts} | WD: {os.getcwd()} | Status: {status}\n"
20:     
21:     paths = [os.path.expanduser("~/.preflight.log"), "./tmp/last_preflight.log"]
22:     for p in paths:
23:         try:
24:             os.makedirs(os.path.dirname(p), exist_ok=True)
25:             with open(p, "a", encoding="utf-8") as f:
26:                 f.write(log_msg)
27:         except Exception:
28:             pass
29:     return ts
30: 
31: def run_step(name, func, *args):
32:     try:
33:         return name, func(*args)
34:     except Exception as e:
35:         return name, f"ERROR: {e}"
36: 
37: def step_quota():
38:     out, code = run_cmd(["ag-quota", "--all", "-j"])
39:     if code == 0 and out:
40:         try:
41:             data = json.loads(out)
42:             snapshot = {}
43:             warnings = []
44:             if isinstance(data, list):
45:                 for acct in data:
46:                     email = acct.get("email") or acct.get("quota_summary", {}).get("Email", "unknown")
47:                     models = acct.get("quota_summary", {})
<truncated 2905 bytes>
ipts/check_thread_bloat.py"), "-j"])
98:     return f"thread bloat status: {'WARNING (Bloated)' if 'true' in out.lower() else 'OK'}" if code == 0 else "thread bloat status: OK"
99: 
100: def step_git():
101:     if os.path.exists(".git"):
102:         _, diff_code = run_cmd(["git", "diff", "--quiet"])
103:         _, status_code = run_cmd(["git", "diff", "--cached", "--quiet"])
104:         cmd = ["git", "pull", "--rebase"] if diff_code != 0 or status_code != 0 else ["git", "pull"]
105:         out, _ = run_cmd(cmd)
106:         return f"Git pull finished: {out[:50]}"
107:     return "Git pull skipped"
108: 
109: def main():
110:     import argparse
111:     parser = argparse.ArgumentParser()
112:     parser.add_argument("--role", default="orchestrator", choices=["orchestrator", "leaf"], help="Agent role")
113:     args = parser.parse_args()
114: 
115:     log_preflight("STARTED")
116:     print("=== PRE-FLIGHT CHECK ===")
117:     
118:     steps = [
119:         ("Quota", step_quota),
120:         ("Jules Quota", step_jules_quota),
121:         ("Task Triager", lambda: step_triage(args.role)),
122:         ("LiteLLM", step_litellm),
123:         ("Rules", step_rules),
124:         ("Thread Bloat", step_bloat),
125:         ("Git", step_git)
126:     ]
127:     
128:     results = {}
129:     with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
130:         future_to_step = {executor.submit(run_step, name, func): name for name, func in steps}
131:         for future in concurrent.futures.as_completed(future_to_step):
132:             name, result = future.result()
133:             results[name] = result
134:             
135:     for name, _ in steps:
136:         print(f"\n--- {name} ---")
137:         print(results[name])
138: 
139:     ts = log_preflight("COMPLETED")
140:     print(f"\n[PREFLIGHT LOGGED] Timestamp: {ts} | Written to ~/.preflight.log")
141: 
142: if __name__ == "__main__":
143:     main()
144: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T21:48:39-06:00
Completed At: 2026-07-31T21:48:39-06:00
File Path: `file:///Users/matt/projects/ai-os/.rules/common.md`
Total Lines: 200
Total Bytes: 29103
Showing lines 1 to 200
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Core Project Rules & System Instructions
2: 
3: ## Auto-Commit Protocol
4: - **Git Auto-Pull & Pre-Flight:** Agents MUST run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` synchronously at the very start of every session/turn, MUST wait for it to complete, and MUST respect its outputs before taking any further actions.
5: - **Jules Delegation:** Agents MUST NEVER force or automatically delegate tasks to Jules. If preflight suggests using Jules (`Use Jules: True`), the agent MUST STOP and ask the user for explicit confirmation before invoking Jules.
6: - **Auto-Commit:** Run `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py` to delegate the commit process. Auto-commit automatically requires a descriptive commit message detailing the changes made (generated via LiteLLM from staged diff/files) and pushes the commits (`git push`) to the remote repository.
7: 
8: ## Project Detection
9: 1. **Root Rule:** A "Project Root" is the nearest ancestor containing a `.git` folder, `package.json`, `Cargo.toml`, `requirements.txt`, or `go.mod`.
10: 2. **Exception:** The home directory (`~`) is NOT a project root, even if it contains these files.
11: 3. **Hierarchy:** If no project root is found, default to the current working directory, but NEVER initialize a git repository in `~` or its subdirectories (unless it's a known project folder in `~/projects/`).
12: 
13: ## Core Rules
14: 1. **Context:** Read `AG_CONTEXT.md` at the project root before ANY work. If missing, create it at the root. Update it with durable knowledge (bullets only) after significant architectural c
<truncated 26425 bytes>
or running a clean test, use `mcp_chrome-devtools_new_page` to spawn a fresh tab rather than hijacking an existing one. Work exclusively within that new tab.
179: |- **Tmux Guardrail:** NEVER run `tmux kill-session` or forcefully terminate the `subagents` tmux session. The user actively monitors this session, and killing it ejects them.
180: 
181: ## Model Override via `{MODEL=...}` in Delegation Prompts
182: 
183: The agy-proxy (port 8080) supports per-call model overrides for `delegate_task`. To use:
184: 
185: 1. Embed `{MODEL=<alias>}` anywhere in a `delegate_task` prompt string.
186: 2. The proxy strips the tag before the prompt reaches the LLM.
187: 3. The alias is passed as `--model <alias>` to agy.
188: 
189: **Configuration:** `delegation.model` in Hermes config must be set to `subagent` (the placeholder that triggers override resolution). Run `hermes config set delegation.model subagent` to enable.
190: 
191: **Fallback:** If `delegation.model` is `"subagent"` but no `{MODEL=...}` tag is found in the prompt, agy runs with its default model (no `--model` flag).
192: 
193: **Valid aliases:** `agy`, `gemini-3.6-flash-low`, `gemini-3.6-flash-medium`, `gemini-3.6-flash-high`, `gemini-3.1-pro-low`, `gemini-3.1-pro-high`, `claude-sonnet-4-6`, `claude-opus-4-6-thinking`, `gpt-oss-120b-medium`.
194: 
195: **Example:** `delegate_task(context="{MODEL=claude-sonnet-4-6} Review this PR...")` → proxy routes to claude-sonnet-4-6.
196: 
197: ## Google Jules Agent Delegation
198: - **Strict Prohibition on `jules` CLI:** Agents MUST NEVER invoke the `jules` CLI binary (`jules new`, `jules remote`, `jules login`, etc.) directly, because it launches interactive terminal TUI frames that hang non-interactive agent sessions.
199: - **REST Script Usage:** ALL Jules delegation, session management, and quota checks MUST strictly route through `python3 ~/projects/ai-os/scripts/jules_delegate.py`, `jules_provisioner.py`, or `jules_quota.py`.
200: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T21:48:39-06:00
Completed At: 2026-07-31T21:48:39-06:00
File Path: `file:///Users/matt/projects/ai-os/.rules/subagent_leaf.md`
Total Lines: 10
Total Bytes: 556
Showing lines 1 to 10
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Leaf Subagent Constraints
2: 
3: ## Execution Constraints
4: 1. **Direct Action:** Execute requested file edits or research directly.
5: 2. **Synchronous Subagents:** Subagent scripts execute synchronously.
6: 3. **No Quoted Heredocs:** Do not use `cat << 'EOF'`. Use file tools directly.
7: 4. **Strict File Reading:** Use `view_file` or `read_lines` tools for surgical inspections.
8: 5. **Strict Output Truncation:** Cap command outputs to 1,000 tokens / 4,000 characters.
9: 6. **No Transient Artifacts:** Keep checklists internal, do not generate transient planning files.
10: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T21:48:39-06:00
Completed At: 2026-07-31T21:48:39-06:00
File Path: `file:///Users/matt/projects/ai-os/.rules/core_safety.md`
Total Lines: 22
Total Bytes: 2433
Showing lines 1 to 22
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Core Safety & Environment Rules
2: 
3: ## Project Detection
4: 1. **Root Rule:** A "Project Root" is the nearest ancestor containing a `.git` folder, `package.json`, `Cargo.toml`, `requirements.txt`, or `go.mod`.
5: 2. **Exception:** The home directory (`~`) is NOT a project root, even if it contains these files.
6: 3. **Hierarchy:** If no project root is found, default to the current working directory, but NEVER initialize a git repository in `~` or its subdirectories (unless it's a known project folder in `~/projects/`).
7: 
8: ## Core Rules
9: 1. **Context:** Read `AG_CONTEXT.md` at the project root before ANY work. If missing, create it at the root. Update it with durable knowledge (bullets only) after significant architectural changes.
10: 2. **Safety:** NEVER use `rm`. ALWAYS use `mv [path] ~/.Trash/` (Exception: `node_modules`).
11: 3. **Tooling:** ALWAYS use `bun`. NEVER use `npm` or `pnpm`. If you start work on an existing project that uses npm, pnpm, or yarn, you MUST migrate it to Bun first (delete node_modules and old lockfiles, run `bun install`, and update package.json scripts) before starting your main task.
12: 4. **Privacy:** ALL generated GitHub repos MUST use `--private`.
13: 5. **No Repo in ~:** NEVER initialize a git repository in the home directory (`~`).
14: 6. **Local Temp:** NEVER use system-level `/tmp`. ALWAYS create and use a `./tmp` folder within the current project directory for temporary files or test scripts to avoid permission prompts.
15: 7. **Directory Consideration & Target Folders:** When asked to create files, utilities, or projects, NEVER litter them directly in generic parent directories (e.g. `~/projects` or a non-project root directory). First consider the current directory: if it is a generic container directory, you MUST create a dedicated sub-directory, move into it, and place all new files and initialize repositories inside that sub-directory.
16:    - **No-Workspace Fallback:** When running without an active workspace open, NEVER create projects inside `~/.gemini/antigravity/scratch/`. ALWAYS create new project directories in `~/projects/<project-name>`.
17: 
18: ## Path Migration Guardrail
19: - **Context**: The host machine migrated from username `matthewmurphy` to `matt`.
20: - **Constraint**: When parsing, reading, creating, or writing absolute paths, files, scripts, or configuration settings:
21:   - ALWAYS translate paths containing `/Users/matthewmurphy/` to `/Users/matt/` (or use relative paths or `~/`).
22: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T21:48:39-06:00
Completed At: 2026-07-31T21:48:39-06:00
File Path: `file:///Users/matt/projects/ai-os/scripts/triage_task.py`
Total Lines: 121
Total Bytes: 5464
Showing lines 1 to 121
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: #!/usr/bin/env python3
2: import os
3: import sys
4: import json
5: import argparse
6: from pathlib import Path
7: 
8: # Add scripts directory to sys.path
9: sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
10: 
11: from jules_quota import get_jules_status
12: from compile_dynamic_prompt import compile_prompt
13: 
14: def evaluate_triage(prompt, files=None, role="orchestrator"):
15:     prompt_lower = prompt.lower()
16:     files = files or []
17: 
18:     # 1. Inspect Quotas
19:     jules_status = get_jules_status()
20:     jules_avail = jules_status.get("total_remaining", 0) if jules_status.get("status") == "OK" else 0
21: 
22:     ag_quota_snapshot = {}
23:     snapshot_path = os.path.expanduser("~/.ag_quota_snapshot.json")
24:     if os.path.exists(snapshot_path):
25:         try:
26:             with open(snapshot_path) as f:
27:                 ag_quota_snapshot = json.load(f)
28:         except Exception:
29:             pass
30: 
31:     # Evaluate local quota pressure
32:     low_local_quota = any(val < 0.20 for val in ag_quota_snapshot.values()) if ag_quota_snapshot else True
33: 
34:     # 2. Keyword & Task Characteristic Matching
35:     keywords_heavy = ["refactor", "unit test", "tests", "boilerplate", "migrate", "docs", "documentation", "feature"]
36:     keywords_quick = ["typo", "fix typo", "rename", "format", "single line", "bugfix"]
37: 
38:     is_heavy_task = any(kw in prompt_lower for kw in keywords_heavy) or len(files) > 3
39:     is_quick_task = any(kw in prompt_lower for kw in keywords_quick) and len(files) <= 1
40: 
41:     # 3. Dec
<truncated 2396 bytes>
 is_quick_task:
83:         decision["engine"] = "local"
84:         decision["recommended_model"] = "gemini-3.5-flash-lite"
85:         decision["reasoning"].append("Quick inline micro-edit detected. Executing locally on fast Flash-Lite tier.")
86:     else:
87:         decision["engine"] = "local"
88:         decision["recommended_model"] = "muse-spark-1.1"
89:         decision["reasoning"].append("Standard interactive task. Executing locally via primary daily driver model.")
90: 
91:     if decision["use_jules"]:
92:         rec_msg = "RECOMMENDATION: Preflight suggests Jules offloading. DO NOT AUTO-OFFLOAD. STOP AND ASK THE USER FOR CONFIRMATION."
93:         if rec_msg not in decision["reasoning"]:
94:             decision["reasoning"].append(rec_msg)
95: 
96:     return decision
97: 
98: def main():
99:     parser = argparse.ArgumentParser(description="Automated Task Triaging Engine")
100:     parser.add_argument("--prompt", required=True, help="User prompt or task description")
101:     parser.add_argument("--files", nargs="*", help="Files involved in task")
102:     parser.add_argument("--json", action="store_true", help="Output JSON format")
103: 
104:     args = parser.parse_args()
105:     decision = evaluate_triage(args.prompt, args.files)
106: 
107:     if args.json:
108:         print(json.dumps(decision, indent=2))
109:     else:
110:         print("=== TASK TRIAGE DECISION ===")
111:         print(f"Recommended Engine: {decision['engine'].upper()} ({decision['recommended_model']})")
112:         print(f"Use Jules: {decision['use_jules']} (Fan-out: {decision['jules_fanout']})")
113:         if decision["auto_context_files"]:
114:             print(f"Auto-Injected Context: {', '.join([os.path.basename(f) for f in decision['auto_context_files']])}")
115:         print("Reasoning:")
116:         for r in decision["reasoning"]:
117:             print(f"  - {r}")
118: 
119: if __name__ == "__main__":
120:     main()
121: 
The above content shows the entire, complete file contents of the requested file.

---

## User

continue

---

## Assistant

Created At: 2026-07-31T21:48:49-06:00
Completed At: 2026-07-31T21:48:49-06:00
File Path: `file:///Users/matt/projects/ai-os/scripts/build_rules.py`
Total Lines: 86
Total Bytes: 3077
Showing lines 1 to 86
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: #!/usr/bin/env python3
2: """
3: build_rules.py - Single Source Rule Bundler for ai-os
4: 
5: Combines modular rules from .rules/ into destination targets:
6:   - CLAUDE.md = common.md + claude_only.md
7:   - GEMINI.md = common.md + gemini_only.md (written to ~/.gemini/GEMINI.md and synced to ~/projects/ai-os/AGENTS.md)
8:   - HERMES.md = common.md + hermes_only.md (written to ~/projects/ai-os/HERMES.md and ~/.hermes/HERMES.md)
9: """
10: 
11: import os
12: from pathlib import Path
13: from compile_dynamic_prompt import compile_prompt
14: 
15: PROJECT_ROOT = Path("/Users/matt/projects/ai-os")
16: RULES_DIR = PROJECT_ROOT / ".rules"
17: 
18: COMMON_PATH = RULES_DIR / "common.md"
19: CLAUDE_ONLY_PATH = RULES_DIR / "claude_only.md"
20: GEMINI_ONLY_PATH = RULES_DIR / "gemini_only.md"
21: HERMES_ONLY_PATH = RULES_DIR / "hermes_only.md"
22: 
23: CLAUDE_TARGET = PROJECT_ROOT / "CLAUDE.md"
24: GEMINI_TARGET = Path("/Users/matt/.gemini/GEMINI.md")
25: HERMES_TARGET_PROJECT = PROJECT_ROOT / "HERMES.md"
26: HERMES_TARGET_GLOBAL = Path("/Users/matt/.hermes/HERMES.md")
27: 
28: def read_file(path: Path) -> str:
29:     if not path.exists():
30:         return ""
31:     with open(path, "r", encoding="utf-8") as f:
32:         return f.read().strip()
33: 
34: def write_file(path: Path, content: str):
35:     path.parent.mkdir(parents=True, exist_ok=True)
36:     if path.exists():
37:         try:
38:             os.chmod(path, 0o644)
39:         except Exception:
40:             pass
41:     with open(path, "w", encoding="utf-8") as f:
42:         f.write(content + "\n")
43:     try:
44:         os.chmod(path, 0o444)
45:     except Exception:
46:         pass
47:     print(f"✅ Generated (Protected 444): {path}")
48: 
49: def main():
50:     # common = read_file(COMMON_PATH)
51:     # claude_only = read_file(CLAUDE_ONLY_PATH)
52:     # gemini_only = read_file(GEMINI_ONLY_PATH)
53:     # hermes_only = read_file(HERMES_ONLY_PATH)
54: 
55:     # Build CLAUDE.md
56:     claude_content = compile_prompt(role="orchestrator", platform="claude", stub=True)
57:     write_file(CLAUDE_TARGET, claude_content)
58: 
59:     # Build GEMINI.md
60:     gemini_content = compile_prompt(role="orchestrator", platform="antigravity", stub=True)
61:     write_file(GEMINI_TARGET, gemini_content)
62: 
63:     # Build HERMES.md
64:     hermes_content = compile_prompt(role="orchestrator", platform="hermes", stub=True)
65:     write_file(HERMES_TARGET_PROJECT, hermes_content)
66:     write_file(HERMES_TARGET_GLOBAL, hermes_content)
67: 
68:     # Sync skills across Hermes, Claude, Antigravity, agy, Codex
69:     sync_skills_script = PROJECT_ROOT / "scripts" / "sync_skills.py"
70:     if sync_skills_script.exists():
71:         os.system(f"python3 {sync_skills_script}")
72: 
73:     # Maintain single clean symlink for AGENTS.md -> GEMINI.md if missing or broken
74:     agents_symlink = PROJECT_ROOT / "AGENTS.md"
75:     if agents_symlink.is_symlink() or not agents_symlink.exists():
76:         try:
77:             if agents_symlink.exists() or agents_symlink.is_symlink():
78:                 agents_symlink.unlink()
79:             agents_symlink.symlink_to(GEMINI_TARGET)
80:             print(f"✅ Symlinked: {agents_symlink} -> {GEMINI_TARGET}")
81:         except Exception as e:
82:             print(f"Warning creating symlink: {e}")
83: 
84: if __name__ == "__main__":
85:     main()
86: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T21:48:54-06:00
Completed At: 2026-07-31T21:48:54-06:00
File Path: `file:///Users/matt/projects/ai-os/scripts/build_rules.py`
Total Lines: 86
Total Bytes: 3077
Showing lines 1 to 86
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: #!/usr/bin/env python3
2: """
3: build_rules.py - Single Source Rule Bundler for ai-os
4: 
5: Combines modular rules from .rules/ into destination targets:
6:   - CLAUDE.md = common.md + claude_only.md
7:   - GEMINI.md = common.md + gemini_only.md (written to ~/.gemini/GEMINI.md and synced to ~/projects/ai-os/AGENTS.md)
8:   - HERMES.md = common.md + hermes_only.md (written to ~/projects/ai-os/HERMES.md and ~/.hermes/HERMES.md)
9: """
10: 
11: import os
12: from pathlib import Path
13: from compile_dynamic_prompt import compile_prompt
14: 
15: PROJECT_ROOT = Path("/Users/matt/projects/ai-os")
16: RULES_DIR = PROJECT_ROOT / ".rules"
17: 
18: COMMON_PATH = RULES_DIR / "common.md"
19: CLAUDE_ONLY_PATH = RULES_DIR / "claude_only.md"
20: GEMINI_ONLY_PATH = RULES_DIR / "gemini_only.md"
21: HERMES_ONLY_PATH = RULES_DIR / "hermes_only.md"
22: 
23: CLAUDE_TARGET = PROJECT_ROOT / "CLAUDE.md"
24: GEMINI_TARGET = Path("/Users/matt/.gemini/GEMINI.md")
25: HERMES_TARGET_PROJECT = PROJECT_ROOT / "HERMES.md"
26: HERMES_TARGET_GLOBAL = Path("/Users/matt/.hermes/HERMES.md")
27: 
28: def read_file(path: Path) -> str:
29:     if not path.exists():
30:         return ""
31:     with open(path, "r", encoding="utf-8") as f:
32:         return f.read().strip()
33: 
34: def write_file(path: Path, content: str):
35:     path.parent.mkdir(parents=True, exist_ok=True)
36:     if path.exists():
37:         try:
38:             os.chmod(path, 0o644)
39:         except Exception:
40:             pass
41:     with open(path, "w", encoding="utf-8") as f:
42:         f.write(content + "\n")
43:     try:
44:         os.chmod(path, 0o444)
45:     except Exception:
46:         pass
47:     print(f"✅ Generated (Protected 444): {path}")
48: 
49: def main():
50:     # common = read_file(COMMON_PATH)
51:     # claude_only = read_file(CLAUDE_ONLY_PATH)
52:     # gemini_only = read_file(GEMINI_ONLY_PATH)
53:     # hermes_only = read_file(HERMES_ONLY_PATH)
54: 
55:     # Build CLAUDE.md
56:     claude_content = compile_prompt(role="orchestrator", platform="claude", stub=True)
57:     write_file(CLAUDE_TARGET, claude_content)
58: 
59:     # Build GEMINI.md
60:     gemini_content = compile_prompt(role="orchestrator", platform="antigravity", stub=True)
61:     write_file(GEMINI_TARGET, gemini_content)
62: 
63:     # Build HERMES.md
64:     hermes_content = compile_prompt(role="orchestrator", platform="hermes", stub=True)
65:     write_file(HERMES_TARGET_PROJECT, hermes_content)
66:     write_file(HERMES_TARGET_GLOBAL, hermes_content)
67: 
68:     # Sync skills across Hermes, Claude, Antigravity, agy, Codex
69:     sync_skills_script = PROJECT_ROOT / "scripts" / "sync_skills.py"
70:     if sync_skills_script.exists():
71:         os.system(f"python3 {sync_skills_script}")
72: 
73:     # Maintain single clean symlink for AGENTS.md -> GEMINI.md if missing or broken
74:     agents_symlink = PROJECT_ROOT / "AGENTS.md"
75:     if agents_symlink.is_symlink() or not agents_symlink.exists():
76:         try:
77:             if agents_symlink.exists() or agents_symlink.is_symlink():
78:                 agents_symlink.unlink()
79:             agents_symlink.symlink_to(GEMINI_TARGET)
80:             print(f"✅ Symlinked: {agents_symlink} -> {GEMINI_TARGET}")
81:         except Exception as e:
82:             print(f"Warning creating symlink: {e}")
83: 
84: if __name__ == "__main__":
85:     main()
86: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T21:48:54-06:00
Completed At: 2026-07-31T21:48:54-06:00
File Path: `file:///Users/matt/projects/ai-os/.rules/subagent_leaf.md`
Total Lines: 10
Total Bytes: 556
Showing lines 1 to 10
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Leaf Subagent Constraints
2: 
3: ## Execution Constraints
4: 1. **Direct Action:** Execute requested file edits or research directly.
5: 2. **Synchronous Subagents:** Subagent scripts execute synchronously.
6: 3. **No Quoted Heredocs:** Do not use `cat << 'EOF'`. Use file tools directly.
7: 4. **Strict File Reading:** Use `view_file` or `read_lines` tools for surgical inspections.
8: 5. **Strict Output Truncation:** Cap command outputs to 1,000 tokens / 4,000 characters.
9: 6. **No Transient Artifacts:** Keep checklists internal, do not generate transient planning files.
10: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T21:48:54-06:00
Completed At: 2026-07-31T21:48:54-06:00
File Path: `file:///Users/matt/projects/ai-os/.rules/core_safety.md`
Total Lines: 22
Total Bytes: 2433
Showing lines 1 to 22
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Core Safety & Environment Rules
2: 
3: ## Project Detection
4: 1. **Root Rule:** A "Project Root" is the nearest ancestor containing a `.git` folder, `package.json`, `Cargo.toml`, `requirements.txt`, or `go.mod`.
5: 2. **Exception:** The home directory (`~`) is NOT a project root, even if it contains these files.
6: 3. **Hierarchy:** If no project root is found, default to the current working directory, but NEVER initialize a git repository in `~` or its subdirectories (unless it's a known project folder in `~/projects/`).
7: 
8: ## Core Rules
9: 1. **Context:** Read `AG_CONTEXT.md` at the project root before ANY work. If missing, create it at the root. Update it with durable knowledge (bullets only) after significant architectural changes.
10: 2. **Safety:** NEVER use `rm`. ALWAYS use `mv [path] ~/.Trash/` (Exception: `node_modules`).
11: 3. **Tooling:** ALWAYS use `bun`. NEVER use `npm` or `pnpm`. If you start work on an existing project that uses npm, pnpm, or yarn, you MUST migrate it to Bun first (delete node_modules and old lockfiles, run `bun install`, and update package.json scripts) before starting your main task.
12: 4. **Privacy:** ALL generated GitHub repos MUST use `--private`.
13: 5. **No Repo in ~:** NEVER initialize a git repository in the home directory (`~`).
14: 6. **Local Temp:** NEVER use system-level `/tmp`. ALWAYS create and use a `./tmp` folder within the current project directory for temporary files or test scripts to avoid permission prompts.
15: 7. **Directory Consideration & Target Folders:** When asked to create files, utilities, or projects, NEVER litter them directly in generic parent directories (e.g. `~/projects` or a non-project root directory). First consider the current directory: if it is a generic container directory, you MUST create a dedicated sub-directory, move into it, and place all new files and initialize repositories inside that sub-directory.
16:    - **No-Workspace Fallback:** When running without an active workspace open, NEVER create projects inside `~/.gemini/antigravity/scratch/`. ALWAYS create new project directories in `~/projects/<project-name>`.
17: 
18: ## Path Migration Guardrail
19: - **Context**: The host machine migrated from username `matthewmurphy` to `matt`.
20: - **Constraint**: When parsing, reading, creating, or writing absolute paths, files, scripts, or configuration settings:
21:   - ALWAYS translate paths containing `/Users/matthewmurphy/` to `/Users/matt/` (or use relative paths or `~/`).
22: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T21:48:56-06:00
Completed At: 2026-07-31T21:48:56-06:00
File Path: `file:///Users/matt/projects/ai-os/HERMES.md`
Total Lines: 4
Total Bytes: 179
Showing lines 1 to 4
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Antigravity Dynamic Context Stub
2: Run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` at session start to retrieve your full system directive if not already provided.
3: 
4: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T21:49:02-06:00
Completed At: 2026-07-31T21:49:02-06:00
File Path: `file:///Users/matt/projects/ai-os/scripts/triage_task.py`
Total Lines: 121
Total Bytes: 5464
Showing lines 1 to 121
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: #!/usr/bin/env python3
2: import os
3: import sys
4: import json
5: import argparse
6: from pathlib import Path
7: 
8: # Add scripts directory to sys.path
9: sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
10: 
11: from jules_quota import get_jules_status
12: from compile_dynamic_prompt import compile_prompt
13: 
14: def evaluate_triage(prompt, files=None, role="orchestrator"):
15:     prompt_lower = prompt.lower()
16:     files = files or []
17: 
18:     # 1. Inspect Quotas
19:     jules_status = get_jules_status()
20:     jules_avail = jules_status.get("total_remaining", 0) if jules_status.get("status") == "OK" else 0
21: 
22:     ag_quota_snapshot = {}
23:     snapshot_path = os.path.expanduser("~/.ag_quota_snapshot.json")
24:     if os.path.exists(snapshot_path):
25:         try:
26:             with open(snapshot_path) as f:
27:                 ag_quota_snapshot = json.load(f)
28:         except Exception:
29:             pass
30: 
31:     # Evaluate local quota pressure
32:     low_local_quota = any(val < 0.20 for val in ag_quota_snapshot.values()) if ag_quota_snapshot else True
33: 
34:     # 2. Keyword & Task Characteristic Matching
35:     keywords_heavy = ["refactor", "unit test", "tests", "boilerplate", "migrate", "docs", "documentation", "feature"]
36:     keywords_quick = ["typo", "fix typo", "rename", "format", "single line", "bugfix"]
37: 
38:     is_heavy_task = any(kw in prompt_lower for kw in keywords_heavy) or len(files) > 3
39:     is_quick_task = any(kw in prompt_lower for kw in keywords_quick) and len(files) <= 1
40: 
41:     # 3. Dec
<truncated 2396 bytes>
 is_quick_task:
83:         decision["engine"] = "local"
84:         decision["recommended_model"] = "gemini-3.5-flash-lite"
85:         decision["reasoning"].append("Quick inline micro-edit detected. Executing locally on fast Flash-Lite tier.")
86:     else:
87:         decision["engine"] = "local"
88:         decision["recommended_model"] = "muse-spark-1.1"
89:         decision["reasoning"].append("Standard interactive task. Executing locally via primary daily driver model.")
90: 
91:     if decision["use_jules"]:
92:         rec_msg = "RECOMMENDATION: Preflight suggests Jules offloading. DO NOT AUTO-OFFLOAD. STOP AND ASK THE USER FOR CONFIRMATION."
93:         if rec_msg not in decision["reasoning"]:
94:             decision["reasoning"].append(rec_msg)
95: 
96:     return decision
97: 
98: def main():
99:     parser = argparse.ArgumentParser(description="Automated Task Triaging Engine")
100:     parser.add_argument("--prompt", required=True, help="User prompt or task description")
101:     parser.add_argument("--files", nargs="*", help="Files involved in task")
102:     parser.add_argument("--json", action="store_true", help="Output JSON format")
103: 
104:     args = parser.parse_args()
105:     decision = evaluate_triage(args.prompt, args.files)
106: 
107:     if args.json:
108:         print(json.dumps(decision, indent=2))
109:     else:
110:         print("=== TASK TRIAGE DECISION ===")
111:         print(f"Recommended Engine: {decision['engine'].upper()} ({decision['recommended_model']})")
112:         print(f"Use Jules: {decision['use_jules']} (Fan-out: {decision['jules_fanout']})")
113:         if decision["auto_context_files"]:
114:             print(f"Auto-Injected Context: {', '.join([os.path.basename(f) for f in decision['auto_context_files']])}")
115:         print("Reasoning:")
116:         for r in decision["reasoning"]:
117:             print(f"  - {r}")
118: 
119: if __name__ == "__main__":
120:     main()
121: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T21:49:02-06:00
Completed At: 2026-07-31T21:49:02-06:00
File Path: `file:///Users/matt/projects/ai-os/.rules/common.md`
Total Lines: 200
Total Bytes: 29103
Showing lines 1 to 50
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Core Project Rules & System Instructions
2: 
3: ## Auto-Commit Protocol
4: - **Git Auto-Pull & Pre-Flight:** Agents MUST run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` synchronously at the very start of every session/turn, MUST wait for it to complete, and MUST respect its outputs before taking any further actions.
5: - **Jules Delegation:** Agents MUST NEVER force or automatically delegate tasks to Jules. If preflight suggests using Jules (`Use Jules: True`), the agent MUST STOP and ask the user for explicit confirmation before invoking Jules.
6: - **Auto-Commit:** Run `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py` to delegate the commit process. Auto-commit automatically requires a descriptive commit message detailing the changes made (generated via LiteLLM from staged diff/files) and pushes the commits (`git push`) to the remote repository.
7: 
8: ## Project Detection
9: 1. **Root Rule:** A "Project Root" is the nearest ancestor containing a `.git` folder, `package.json`, `Cargo.toml`, `requirements.txt`, or `go.mod`.
10: 2. **Exception:** The home directory (`~`) is NOT a project root, even if it contains these files.
11: 3. **Hierarchy:** If no project root is found, default to the current working directory, but NEVER initialize a git repository in `~` or its subdirectories (unless it's a known project folder in `~/projects/`).
12: 
13: ## Core Rules
14: 1. **Context:** Read `AG_CONTEXT.md` at the project root before ANY work. If missing, create it at the root. Update it with durable knowledge (bullets only) after significant architectural ch
<truncated 8339 bytes>
i/GEMINI.md)`), while the target URL inside `(...)` MUST remain the valid absolute `file:///...` path so clicking works perfectly. Plain text unlinked file paths and verbose un-shortened absolute link labels are strictly prohibited.
42: 25. **Background Service Registration & `la` Protocol:** ANY new background daemon, service, or URL scheme listener created for macOS MUST have a corresponding launch agent plist in `~/Library/LaunchAgents/` that is registered in `la` (`~/.local/bin/la`) and wrapped inside a `tmux` session (e.g. via `tmux-agent-wrapper.sh`) so its status, PID, and live execution logs can be monitored cleanly via `la status <name>` and `la logs <name>`.
43: 
44: ## Helper Utilities Directory & Agent Tooling
45: When performing standard system actions, agents SHOULD prefer calling established local helper scripts in `~/projects/ai-os/scripts/` over raw manual implementations:
46: - **`subagent.py`**: Invokes subagents with model validation against `litellm/config.yaml`. (e.g. `python3 ~/projects/ai-os/scripts/subagent.py -p "<prompt>" -m <model>`)
47: - **`clip_search.py`**: Searches macOS clipboard history when referenced code/links are missing from context. (e.g. `python3 ~/projects/ai-os/scripts/clip_search.py "<query>"`)
48: - **`search_all_agent_logs.py`**: Searches across all past `agent-logs/` history to review prior attempts/fixes. (e.g. `python3 ~/projects/ai-os/scripts/search_all_agent_logs.py "<query>"`)
49: - **`generate_repo_map.py`**: Generates a token-efficient visual directory/code structure map for large repositories. (e.g. `python3 ~/projects/ai-os/scripts/generate_repo_map.py`)
50: - **`precision_edit.py`**: Performs surgical micro-edits/replacements on files without full rewrites. (e.g. `python3 ~/projects/ai-os/scripts/precision_edit.py <file> <action> --target "<target>" --content "<content>"`)
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-07-31T21:49:02-06:00
Completed At: 2026-07-31T21:49:03-06:00
File Path: `file:///Users/matt/projects/ai-os/.rules/hermes_only.md`
Total Lines: 12
Total Bytes: 1197
Showing lines 1 to 12
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: ## Hermes Agent Specific Rules
2: 
3: ## Economic Thread & Context Management
4: - **Token Math & Handoff Rule:** Evaluate accumulated conversation tokens ($T_{\text{hist}}$) against system baseline ($T_{\text{sys}}$). When $T_{\text{hist}}$ exceeds $T_{\text{hist\_threshold}}$ (~35,000 tokens or >15-20 turns with heavy tool outputs), write a structured context handoff log in `agent-logs/YYYY-MM-DD_HH-MM_description.md` and suggest starting a fresh thread or subagent to preserve token efficiency.
5: 
6: ## Safe System Memory & Skill Protection
7: - **No System File Overwrites:** Never overwrite Hermes Agent's internal system configuration files, system prompt definitions, or system-generated metadata files during self-learning or memory updates.
8: - **Memory & Skill Protocol:** Use native `memory(target='user')` and `memory(target='memory')` tool calls for durable facts and preferences. Use `skill_manage` to record reusable procedural workflows into skills.
9: 
10: ## Post-Edit Reload Protocol
11: - **Hammerspoon Reload Rule:** Whenever you modify any source or HTML/Lua file in `qwerty-midi-hammerspoon`, run `./bin/bundle_and_reload.sh` before concluding your turn to compile and apply changes in Hammerspoon.
12: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T21:49:03-06:00
Completed At: 2026-07-31T21:49:03-06:00
File Path: `file:///Users/matt/projects/ai-os/.rules/gemini_only.md`
Total Lines: 109
Total Bytes: 7892
Showing lines 1 to 109
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: ## Gemini / Antigravity Specific Rules
2: 
3: - **Mandatory Synchronous Preflight & Waiting:** Agents MUST run preflight at the start of every session, wait for it to complete synchronously, and respect its findings. Agents MUST NEVER force Jules without asking the user first.
4: 
5: ## Mandatory agymcp Delegation Protocol (NO Native Subagents & NO Raw Terminal agy)
6: - **Strict Prohibition**: The main orchestrator (M) MUST NEVER use native Antigravity `invoke_subagent` OR run raw `run_command("agy -p ...")` terminal commands. 
7: - **Mandatory Tool (`agymcp`)**: ALL subagent tasks (Context Fetching, Pro Planning, File Edits, QA Audits) MUST be invoked via the `agymcp` server tools (`agymcp:agy`, `agymcp:agy_continue`, or `agymcp:agy_start`), which manages tmux background sessions cleanly.
8: 
9: ## Flash-Lite Edit Delegation (Antigravity Native)
10: - **Rule:** When running in Antigravity, the top-level orchestrator agent MUST **never write or modify files directly** using `write_to_file`, `replace_file_content`, or `multi_replace_file_content` itself. Instead, it MUST delegate ALL file creation and editing operations to a `flash_lite` subagent. The orchestrator agent MUST NOT fall back to or use `Model: "flash"`; `flash_lite` is the strictly enforced requirement.
11: - **How:** To definitively prevent recursive subagent loops, the orchestrator MUST physically restrict the subagent's tools:
12:   1. Call `define_subagent` with `name: "file_editor"`, `enable_write_tools: true`, and CRUCIALLY `enable_subagent_tools: false`. Include a `system_prompt` explicitly telling it 
<truncated 4763 bytes>
on synchronous probes (`git status`, `which`, `--help`), ALWAYS set `WaitMsBeforeAsync` to at least `5000` (or up to `10000`). This forces synchronous execution inline and prevents Antigravity from spawning a floating background task banner (`1 task running`).
92: - **Post-Flight & Periodic Task Cleanup**: Before concluding a turn after major calls or multi-step tool sequences, check for active background tasks via `manage_task(Action='list')`. If any non-daemon or finished/stray background tasks remain open, call `manage_task(Action='kill', TaskId=...)` to clean them up and keep the UI task bar clear.
93: 
94: - **Batching:** Batch all related file edits into a **single** subagent invocation. Do not spawn one subagent per file.
95: - **Verification:** After the subagent reports completion, run `git diff` once to verify. Do not re-read files unless the diff reveals something unexpected.
96: 
97: ## Post-Edit Reload Protocol
98: - **Hammerspoon Reload Rule:** Whenever you modify any source/Lua file in `qwerty-midi-hammerspoon` (or projects using Hammerspoon bundles), you MUST immediately run `bash /Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh` as a mandatory post-flight step before concluding your turn or declaring the task done.
99: 
100: ## Hermes Operational Emulation & Self-Improvement Protocol (Antigravity Only)
101: When running under Gemini/Antigravity without Hermes' active daemon, you MUST emulate Hermes' core runtime directives:
102: 
103: 1. **Tool-Use Enforcement**:
104:    - You MUST use tools to take action — never describe what you plan to do without executing it in the same turn.
105:    - Responses that only describe intentions ("I will run the tests", "Let me inspect the file") without accompanying tool calls are prohibited.
106: 
107: 2. **Task Completion & Anti-Fabrication**:
108:    - Deliverables must be working artifacts backed by real tool execution output, not prose summaries.
109: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T21:49:03-06:00
Completed At: 2026-07-31T21:49:03-06:00
File Path: `file:///Users/matt/projects/ai-os/.rules/git_protocol.md`
Total Lines: 6
Total Bytes: 659
Showing lines 1 to 6
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Git Protocol Rules
2: 
3: ## Auto-Commit Protocol
4: - **Git Auto-Pull & Pre-Flight:** Before any agent begins work on an established git project, it MUST run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` to perform all pre-flight routines (evaluating `ag-quota` velocity, auto-pulling/rebasing latest git changes, etc.) in a single step.
5: - **Auto-Commit:** Run `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py` to delegate the commit process. Auto-commit automatically requires a descriptive commit message detailing the changes made (generated via LiteLLM from staged diff/files) and pushes the commits (`git push`) to the remote repository.
6: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T21:49:03-06:00
Completed At: 2026-07-31T21:49:03-06:00
File Path: `file:///Users/matt/projects/ai-os/.rules/agent_logs.md`
Total Lines: 9
Total Bytes: 709
Showing lines 1 to 9
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Agent Work Logs & History
2: 
3: ## Agent Work Logs Protocol
4: 0. **Fresh Thread Context & Recent History:** When starting a new thread/session, scan the project root for `AG_CONTEXT.md`, `FEATURES.md`, `DEVELOPMENT_JOURNAL.md`, and `agent-logs/`. Read `DEVELOPMENT_JOURNAL.md` first, then inspect recent logs.
5: 1. **Log Directory:** Maintain `agent-logs/` at the project root.
6: 2. **Reading Logs:** Scan `agent-logs/` for related past work before starting.
7: 3. **Writing Logs:** At the END of every session with code changes, create `agent-logs/YYYY-MM-DD_HH-MM_<description>.md`.
8: 4. **Development Journal:** Append a 2-3 line bullet entry to `DEVELOPMENT_JOURNAL.md` at the project root at the end of every session.
9: 
The above content shows the entire, complete file contents of the requested file.

Here is a concise, rock-solid plan to untangle the rule system and fix the context bloat and unpredictability you're experiencing.

### The Root Cause
Right now, you have a conflicting "split-brain" architecture:
1. **The Monolith vs. The Modules:** You have a massive 29KB `common.md` file containing every rule, but you *also* have modular files (`core_safety.md`, `git_protocol.md`, `agent_logs.md`). They are redundant and out of sync.
2. **The Stub Anti-Pattern:** `build_rules.py` is currently writing **stubs** to `HERMES.md`, `GEMINI.md`, and `CLAUDE.md`, forcing agents to run `preflight.py` to get their instructions.
3. **Dynamic Injection Bloat:** Because the files are stubs, `preflight.py` (via `triage_task.py`) dynamically prints the entire compiled system prompt to `stdout` (`=== INJECTED SYSTEM DIRECTIVE ===`). This burns output tokens, litters the conversation thread, and causes subagents to inherit orchestrator rules.

---

### Step-by-Step Simplification Plan

#### 1. Eliminate the Monolith (`common.md`)
The modular breakdown (`core_safety`, `git_protocol`, `agent_logs`, etc.) is the correct approach. 
* **Action:** Delete `~/.rules/common.md`. Rely entirely on the smaller, focused markdown files.

#### 2. Stop Dynamic Injection in `preflight.py`
System rules should be loaded natively by the host platform (Hermes, Antigravity, Claude Code), not printed to the terminal on every run.
* **Action:** Edit `/Users/matt/projects/ai-os/scripts/triage_task.py`. Remove the code that calls `compile_prompt()` and appends `=== INJECTED SYSTEM DIRECTIVE ===` to the output. `preflight.py` should strictly return quota and git status.

#### 3. Statically Compile Target Files (`build_rules.py`)
Let the IDE/CLI platforms do what they do best: natively read `HERMES.md` / `GEMINI.md` / `CLAUDE.md` as their system prompts silently in the background.
* **Action:** Edit `/Users/matt/projects/ai-os/scripts/build_rules.py` and change `stub=True` to `stub=False` in the `compile_prompt` calls.
* **Result:** `build_rules.py` will now stitch the modular files together and write the *full, actual rules* to `HERMES.md` and `GEMINI.md`.

#### 4. Isolate Leaf Agent Instructions
Subagents don't need to know about GitHub workflows or session logging; they just need to know how to edit files safely.
* **Action:** In `build_rules.py`, add a new build target to statically compile a `LEAF.md` (or `SUBAGENT.md`):
  ```python
  leaf_content = compile_prompt(role="leaf", stub=False)
  write_file(PROJECT_ROOT / "LEAF.md", leaf_content)
  ```
* **Action:** Update your `subagent.py` and `agymcp` tools to explicitly pass `LEAF.md` as the system prompt for child agents, completely bypassing the orchestrator's `AGENTS.md` / `GEMINI.md`.

### Why this architecture is rock-solid:
- **Zero Output Noise:** No more massive rule dumps in the terminal from `preflight.py`.
- **Strict Boundaries:** Orchestrators get `HERMES.md` (orchestrator rules). Subagents get `LEAF.md` (strict execution constraints). No overlap.
- **Single Source of Truth:** You edit the tiny modular files in `.rules/`, run `build_rules.py`, and all platforms instantly get their tailored, non-conflicting instructions.

Created At: 2026-07-31T21:49:20-06:00
Completed At: 2026-07-31T21:49:20-06:00
File Path: `file:///Users/matt/projects/ai-os/HERMES.md`
Total Lines: 4
Total Bytes: 179
Showing lines 1 to 4
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Antigravity Dynamic Context Stub
2: Run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` at session start to retrieve your full system directive if not already provided.
3: 
4: 
The above content shows the entire, complete file contents of the requested file.

I have completed a thorough, ground-up audit of the prompt assembly and rule system across `compile_dynamic_prompt.py`, `preflight.py`, and the `.rules/` directory. 

I see exactly why the system has felt leaky, complex, and unpredictable. Take a deep breath—this is a very solvable architectural knot.

### The Diagnosis: Why it’s breaking
1. **The "Stub + Injection" Anti-Pattern:** Currently, `build_rules.py` generates "stubs" for `HERMES.md` and `GEMINI.md` that force the agent to run `preflight.py`. `preflight.py` then dumps the *actual* system instructions into the terminal stdout. System rules belong in the native system prompt; dumping them into the chat history causes them to slide out of the context window, confusing the LLM and causing it to forget its rules mid-task.
2. **Subagent Identity Crisis:** `AGENTS.md` (which the `agy` leaf workers read) is currently symlinked to `GEMINI.md` (an orchestrator file). This means a cheap, dumb subagent spins up, reads a stub telling it to run a preflight check, and then gets flooded with orchestrator rules. This leads to subagents trying to self-orchestrate, getting stuck in loops, or failing their narrow tasks.
3. **Ghost Files:** There is a massive 29KB `common.md` file sitting in `.rules/` that isn't actually being compiled by the new scripts, but it creates immense confusion about the source of truth versus the modular files (`core_safety.md`, `git_protocol.md`, etc.).

---

### The Solution: A Rock-Solid, Static Architecture
We need to move away from **Runtime Dynamic Injection** to **Static Build-Time Assembly**. System prompts should be statically compiled so agents natively understand their roles the second they wake up, without needing to run a script first.

#### Step 1: Fix `build_rules.py` (Static Assembly)
We will rewrite `build_rules.py` to stop generating stubs. Instead, it will assemble the full rule files directly:
- **Orchestrators (`HERMES.md`, `CLAUDE.md`, `GEMINI.md`)** will get: `core_safety.md` + `git_protocol.md` + `agent_logs.md` + their `[platform]_only.md`. 
- **Leaf Workers (`AGENTS.md`)** will get strictly: `core_safety.md` + `subagent_leaf.md`. We will break the symlink to `GEMINI.md` so subagents are explicitly sandboxed as workers.

#### Step 2: Strip `preflight.py` of Prompt Duties
We will remove `compile_prompt()` from `triage_task.py` and remove the `=== INJECTED SYSTEM DIRECTIVE ===` output from `preflight.py`. 
- `preflight.py` will return to being a true preflight check: it will *only* report API quotas, Git status, and triage recommendations (e.g., "Use Jules", "Use Flash-Lite"). 
- No more rules printed to `stdout`, drastically reducing context bloat.

#### Step 3: Purge Legacy Bloat
- Delete `common.md` entirely. The modular files in `.rules/` (`core_safety.md`, etc.) are your strict, single sources of truth. 
- Eliminate `compile_dynamic_prompt.py` entirely, as its logic will be cleanly absorbed into a much simpler `build_rules.py`. 

### The Master Simplification Plan

If you approve, I will execute this clean-up in one shot:
1. **Delete** `.rules/common.md` and `scripts/compile_dynamic_prompt.py`.
2. **Rewrite** `scripts/build_rules.py` to perform pure static concatenation into the target files.
3. **Rewrite** `scripts/triage_task.py` and `scripts/preflight.py` to strip out all prompt-injection logic, returning them to clean diagnostic tools.
4. **Run** `python3 scripts/build_rules.py` to generate the correct, fully-baked `HERMES.md`, `CLAUDE.md`, `GEMINI.md`, and `AGENTS.md` files.

This will instantly drop the context bloat, stop subagents from hallucinating orchestrator duties, and give every agent a rock-solid, unchanging set of rules native to their environment. 

Would you like me to proceed with executing this plan?

---
