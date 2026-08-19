---
title: "Update Git Protocol Rules"
date: "2026-08-01"
conversation_id: "32234dce-403f-4106-b62d-418caa891873"
source: "antigravity"
---

# Update Git Protocol Rules

## User

You are a file editing subagent. You will apply the following edit using `replace_file_content` to `/Users/matt/.gemini/GEMINI.md`.

Find around line 24:
```markdown
# Git Protocol Rules

## Auto-Commit Protocol
```
Replace with:
```markdown
# Git Protocol Rules

## GitHub Issue Tracking Mandate
- **Strict Requirement:** Agents MUST proactively create GitHub issues for any newly reported bugs, feature requests, or notable architectural plans during a session.
- **Workflow Integration:** Whenever a user mentions a bug or feature, check for existing issues (`gh issue list`). If none exist, create one (`gh issue create`). Update the issue with progress and close it upon completion.

## Auto-Commit Protocol
```

When you are done, report completion.

---

## Assistant

Created At: 2026-08-01T17:12:45-06:00
Completed At: 2026-08-01T17:12:45-06:00

				The command completed successfully.
				Output:
				-r--r--r--@ 1 matt  staff  9909 Aug  1 17:05 /Users/matt/.gemini/GEMINI.md

Created At: 2026-08-01T17:12:45-06:00
Completed At: 2026-08-01T17:12:45-06:00

				The command completed successfully.
				Stdout:
				
				Stderr:

Created At: 2026-08-01T17:12:46-06:00
Completed At: 2026-08-01T17:12:46-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/.gemini/GEMINI.md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -22,6 +22,10 @@
 
 # Git Protocol Rules
 
+## GitHub Issue Tracking Mandate
+- **Strict Requirement:** Agents MUST proactively create GitHub issues for any newly reported bugs, feature requests, or notable architectural plans during a session.
+- **Workflow Integration:** Whenever a user mentions a bug or feature, check for existing issues (`gh issue list`). If none exist, create one (`gh issue create`). Update the issue with progress and close it upon completion.
+
 ## Auto-Commit Protocol
 - **Git Auto-Pull & Pre-Flight:** Before any agent begins work on an established git project, it MUST run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` to perform all pre-flight routines (evaluating `ag-quota` velocity, auto-pulling/rebasing latest git changes, etc.) in a single step.
 - **Auto-Commit:** Run `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py` to delegate the commit process. Auto-commit automatically requires a descriptive commit message detailing the changes made (generated via LiteLLM from staged diff/files) and pushes the commits (`git push`) to the remote repository.
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-01T17:12:47-06:00
Completed At: 2026-08-01T17:12:47-06:00

				The command completed successfully.
				Stdout:
				
				Stderr:

Created At: 2026-08-01T17:12:48-06:00
Completed At: 2026-08-01T17:12:48-06:00
Message sent to "933b2ef1-5f57-4aee-8b1e-130d7bad6a76".

The edit to `/Users/matt/.gemini/GEMINI.md` has been successfully completed. I have added the GitHub Issue Tracking Mandate section to the Git Protocol Rules and restored the file's read-only permissions. I have informed the parent agent of the completion.

---
