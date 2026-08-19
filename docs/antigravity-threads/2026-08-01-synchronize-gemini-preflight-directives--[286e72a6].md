---
title: "Synchronize Gemini Preflight Directives"
date: "2026-08-01"
conversation_id: "286e72a6-1f6e-4673-b894-e7d9043bdeb2"
source: "antigravity"
---

# Synchronize Gemini Preflight Directives

## User

Ensure both /Users/matt/.gemini/GEMINI.md and /Users/matt/projects/ai-os/.gemini/GEMINI.md contain the preflight directive rule cleanly:

```markdown
# Antigravity Dynamic Context Stub
Run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` at session start to retrieve your full system directive if not already provided.
```

Verify both files contain this exact text and report back.

---

## Assistant

Created At: 2026-07-31T21:38:37-06:00
Completed At: 2026-07-31T21:38:37-06:00
{"name":".DS_Store","sizeBytes":"12292"}
{"name":"GEMINI.md","sizeBytes":"179"}
{"name":"antigravity","isDir":true}
{"name":"antigravity-backup","isDir":true}
{"name":"antigravity-cli","isDir":true}
{"name":"antigravity-ide","isDir":true}
{"name":"config","isDir":true}
{"name":"extension_integrity.json","sizeBytes":"294"}
{"name":"extensions","isDir":true}
{"name":"google_accounts.json","sizeBytes":"195"}
{"name":"google_accounts.json.bak","sizeBytes":"195"}
{"name":"history","isDir":true}
{"name":"installation_id","sizeBytes":"36"}
{"name":"oauth_creds.json","sizeBytes":"1811"}
{"name":"oauth_creds.json.bak","sizeBytes":"1572"}
{"name":"projects.json","sizeBytes":"1154"}
{"name":"rules","isDir":true}
{"name":"sessions","isDir":true}
{"name":"settings.json","sizeBytes":"224"}
{"name":"settings.json.bak","sizeBytes":"224"}
{"name":"skills","isDir":true}
{"name":"staging_memories","isDir":true}
{"name":"state.json","sizeBytes":"356"}
{"name":"tmp","isDir":true}
{"name":"trustedFolders.json","sizeBytes":"186"}

Summary: This directory contains 12 subdirectories and 13 files.

Created At: 2026-07-31T21:38:38-06:00
Completed At: 2026-07-31T21:38:38-06:00
{"name":"GEMINI.md","sizeBytes":"1694"}

Summary: This directory contains 0 subdirectories and 1 files.

Created At: 2026-07-31T21:38:39-06:00
Completed At: 2026-07-31T21:38:39-06:00
File Path: `file:///Users/matt/.gemini/GEMINI.md`
Total Lines: 4
Total Bytes: 179
Showing lines 1 to 4
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Antigravity Dynamic Context Stub
2: Run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` at session start to retrieve your full system directive if not already provided.
3: 
4: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T21:38:39-06:00
Completed At: 2026-07-31T21:38:39-06:00
File Path: `file:///Users/matt/projects/ai-os/.gemini/GEMINI.md`
Total Lines: 23
Total Bytes: 1694
Showing lines 1 to 23
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
11: 3. **Tooling:** ALWAYS use `bun`. NEVER use `npm` or `pnpm`.
12: 4. **Privacy:** ALL generated GitHub repos MUST use `--private`.
13: 5. **No Repo in ~:** NEVER initialize a git repository in the home directory (`~`).
14: 6. **Local Temp:** NEVER use system-level `/tmp`. ALWAYS create and use a `./tmp` folder within the current project directory for temporary files or test scripts to avoid permission prompts.
15: 
16: ## Path Migration Guardrail
17: - **Context**: The host machine migrated from username `matthewmurphy` to `matt`.
18: - **Constraint**: ALWAYS translate paths containing `/Users/matthewmurphy/` to `/Users/matt/` (or use relative paths or `~/`).
19: 
20: # Git Protocol Rules
21: - **Pre-Flight:** Agents must run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` at session start.
22: - **Auto-Commit:** Run `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py` for auto-commits.
23: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T21:38:41-06:00
Completed At: 2026-07-31T21:38:41-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/ai-os/.gemini/GEMINI.md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -17,7 +17,9 @@
 - **Context**: The host machine migrated from username `matthewmurphy` to `matt`.
 - **Constraint**: ALWAYS translate paths containing `/Users/matthewmurphy/` to `/Users/matt/` (or use relative paths or `~/`).
 
+# Antigravity Dynamic Context Stub
+Run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` at session start to retrieve your full system directive if not already provided.
+
 # Git Protocol Rules
-- **Pre-Flight:** Agents must run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` at session start.
 - **Auto-Commit:** Run `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py` for auto-commits.
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-07-31T21:38:42-06:00
Completed At: 2026-07-31T21:38:42-06:00
Message sent to "73745207-34ba-472b-8f6f-5afa8086f92e".

The preflight directive rule has been verified and ensured in both files:

1.  **/Users/matt/.gemini/GEMINI.md**: This file already contained the exact text requested.
2.  **/Users/matt/projects/ai-os/.gemini/GEMINI.md**: This file has been updated to include the standard "Antigravity Dynamic Context Stub" directive cleanly, replacing the previous, less formal pre-flight mention.

I have notified the parent agent of these updates.

---
