## Project Detection
1. **Root Rule:** A "Project Root" is the nearest ancestor containing a `.git` folder, `package.json`, `Cargo.toml`, `requirements.txt`, or `go.mod`.
4. **Subdirectory Git Detection:** Scripts and agents must ALWAYS detect git repository roots using `git rev-parse --is-inside-work-tree` and `git rev-parse --show-toplevel` instead of checking `os.path.exists(".git")` in the current working directory.
2. **Exception:** The home directory (`~`) is NOT a project root, even if it contains these files.
3. **Hierarchy & Config Repositories:** If no project root is found, default to the current working directory. NEVER initialize a git repository directly in the bare home root directory (`~`). Standalone tool/configuration suites (e.g. `~/.hammerspoon`) or project folders under `~/projects/` SHOULD and MUST be tracked in their own Git repositories with private remotes, per the Ubiquitous Git Tracking Directive.

# Git Protocol Rules

## Auto-Commit Protocol
- **Git Auto-Pull & Pre-Flight:** Before any agent begins work on an established git project, it MUST run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` to perform all pre-flight routines (evaluating `ag-quota` velocity, auto-pulling/rebasing latest git changes, etc.) in a single step.
- **Auto-Commit & Push:** Whenever an agent concludes work involving code or documentation changes on a git repository, it MUST execute `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py -m "<message>" [--paths <files>]` to stage, commit, and immediately push commits (`git push`) to the remote repository. The agent writes the commit message itself (a specific subject line, plus a short body on *why* when useful); without `-m` the script falls back to a generic "Update <files>" summary. Use `--paths` to commit only this session's files. NEVER leave working tree changes uncommitted or unpushed at task conclusion.
- **Branch Protection & Staging Invariants (Daily Mini-Crossword)**: For `daily-mini-crossword`, all agents and developers MUST work and commit exclusively on the `working` branch. NEVER commit or push directly to `main`. The `main` branch autodeploys to production on Vercel (`crossword.mattmurphy.ca`) and is reserved strictly for official public releases.
- **Make It Live by Default (2026-10-20)**: When Matt asked for a change and it's tested and very likely working, make it live without waiting (merge it where the live job/app runs from, install it, switch it on), then tell him "I made this live; want me to undo it?". Only wait for his approval first when the change is genuinely experimental or likely to fail. Why: a finished change left on a side branch behind an easy-to-miss "should I make it live?" question confused him when the old version kept running. The daily-mini-crossword `main` (public production) rule above still applies.

## Ubiquitous Git Tracking Directive
- **All Code & Configs in Git**: Practically all scripts, tools, configurations, automation modules, dotfiles, and codebases MUST reside inside a Git repository backed by a remote repository (always `--private` by default unless explicitly public).
- **Proactive Untracked File Detection**: Whenever an agent encounters, modifies, or inspects files or scripts that are NOT inside a Git worktree:
  - The agent MUST immediately notify Matt that the files are untracked.
  - The agent MUST assume Matt wants them tracked in a Git repository and either initialize/link a private repo or bring them into an appropriate repository structure.
