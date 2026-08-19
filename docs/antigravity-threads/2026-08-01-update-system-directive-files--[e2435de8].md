---
title: "Update System Directive Files"
date: "2026-08-01"
conversation_id: "e2435de8-4efa-4b26-8a19-75f9d98caafe"
source: "antigravity"
---

# Update System Directive Files

## User

Update /Users/matt/.gemini/GEMINI.md and /Users/matt/projects/ai-os/.gemini/GEMINI.md to include explicit, un-ignorable system directives for orchestrators and preflight:

```markdown
# Antigravity Dynamic Context Stub & Global Directives

## Preflight Requirement
Run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` at session start to retrieve system status and quota.

## Main Thread Response Protocol (Orchestrator Only)
When acting as the main thread orchestrator, you MUST format all non-trivial conversation responses by running `python3 /Users/matt/projects/ai-os/scripts/gen_conversation_md.py <conversation-id> --title "<Title>" --save-turn` and referring the user to [conversation_response.md](file:///Users/matt/.gemini/antigravity/brain/<conversation-id>/conversation_response.md).
Subagents (leaf workers) MUST IGNORE this response artifact protocol and reply directly.
```

Apply this update to both files and report completion.

---

## Assistant

Created At: 2026-07-31T21:39:48-06:00
Completed At: 2026-07-31T21:39:48-06:00
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

Created At: 2026-07-31T21:39:48-06:00
Completed At: 2026-07-31T21:39:48-06:00
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

Created At: 2026-07-31T21:39:49-06:00
Completed At: 2026-07-31T21:39:49-06:00
{"name":"GEMINI.md","sizeBytes":"1763"}

Summary: This directory contains 0 subdirectories and 1 files.

Created At: 2026-07-31T21:39:50-06:00
Completed At: 2026-07-31T21:39:50-06:00
File Path: `file:///Users/matt/projects/ai-os/.gemini/GEMINI.md`
Total Lines: 25
Total Bytes: 1763
Showing lines 1 to 25
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
20: # Antigravity Dynamic Context Stub
21: Run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` at session start to retrieve your full system directive if not already provided.
22: 
23: # Git Protocol Rules
24: - **Auto-Commit:** Run `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py` for auto-commits.
25: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T21:39:52-06:00
Completed At: 2026-07-31T21:39:53-06:00

				The command completed successfully.
				Stdout:
				
				Stderr:

Created At: 2026-07-31T21:39:54-06:00
Completed At: 2026-07-31T21:39:54-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/.gemini/GEMINI.md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -1,4 +1,9 @@
-# Antigravity Dynamic Context Stub
-Run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` at session start to retrieve your full system directive if not already provided.
-
+# Antigravity Dynamic Context Stub & Global Directives
+
+## Preflight Requirement
+Run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` at session start to retrieve system status and quota.
+
+## Main Thread Response Protocol (Orchestrator Only)
+When acting as the main thread orchestrator, you MUST format all non-trivial conversation responses by running `python3 /Users/matt/projects/ai-os/scripts/gen_conversation_md.py <conversation-id> --title "<Title>" --save-turn` and referring the user to [conversation_response.md](file:///Users/matt/.gemini/antigravity/brain/<conversation-id>/conversation_response.md).
+Subagents (leaf workers) MUST IGNORE this response artifact protocol and reply directly.
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

We did our best to apply changes despite some inaccuracies. Double check if the edit applied is what you intended.

Created At: 2026-07-31T21:39:55-06:00
Completed At: 2026-07-31T21:39:55-06:00

				The command completed successfully.
				Stdout:
				
				Stderr:

Created At: 2026-07-31T21:39:56-06:00
Completed At: 2026-07-31T21:39:56-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/ai-os/.gemini/GEMINI.md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -17,8 +17,14 @@
 - **Context**: The host machine migrated from username `matthewmurphy` to `matt`.
 - **Constraint**: ALWAYS translate paths containing `/Users/matthewmurphy/` to `/Users/matt/` (or use relative paths or `~/`).
 
-# Antigravity Dynamic Context Stub
-Run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` at session start to retrieve your full system directive if not already provided.
+# Antigravity Dynamic Context Stub & Global Directives
+
+## Preflight Requirement
+Run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` at session start to retrieve system status and quota.
+
+## Main Thread Response Protocol (Orchestrator Only)
+When acting as the main thread orchestrator, you MUST format all non-trivial conversation responses by running `python3 /Users/matt/projects/ai-os/scripts/gen_conversation_md.py <conversation-id> --title "<Title>" --save-turn` and referring the user to [conversation_response.md](file:///Users/matt/.gemini/antigravity/brain/<conversation-id>/conversation_response.md).
+Subagents (leaf workers) MUST IGNORE this response artifact protocol and reply directly.
 
 # Git Protocol Rules
 - **Auto-Commit:** Run `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py` for auto-commits.
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-07-31T21:39:57-06:00
Completed At: 2026-07-31T21:39:57-06:00
Message sent to "73745207-34ba-472b-8f6f-5afa8086f92e".

The requested updates to `/Users/matt/.gemini/GEMINI.md` and `/Users/matt/projects/ai-os/.gemini/GEMINI.md` have been completed successfully. Both files now contain the required "Antigravity Dynamic Context Stub & Global Directives" section with the preflight requirement and the main thread response protocol.

---
