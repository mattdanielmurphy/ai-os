# Git Protocol Rules

## Auto-Commit Protocol
- **Git Auto-Pull & Pre-Flight:** Before any agent begins work on an established git project, it MUST run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` to perform all pre-flight routines (evaluating `ag-quota` velocity, auto-pulling/rebasing latest git changes, etc.) in a single step.
- **Auto-Commit & Push:** Whenever an agent concludes work involving code or documentation changes on a git repository, it MUST execute `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py` to stage, commit, and immediately push commits (`git push`) to the remote repository. NEVER leave working tree changes uncommitted or unpushed at task conclusion.

## Ubiquitous Git Tracking Directive
- **All Code & Configs in Git**: Practically all scripts, tools, configurations, automation modules, dotfiles, and codebases MUST reside inside a Git repository backed by a remote repository (always `--private` by default unless explicitly public).
- **Proactive Untracked File Detection**: Whenever an agent encounters, modifies, or inspects files or scripts that are NOT inside a Git worktree:
  - The agent MUST immediately notify Matt that the files are untracked.
  - The agent MUST assume Matt wants them tracked in a Git repository and either initialize/link a private repo or bring them into an appropriate repository structure.

