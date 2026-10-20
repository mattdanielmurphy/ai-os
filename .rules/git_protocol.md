# Git Protocol Rules

## Auto-Commit Protocol
- **Git Auto-Pull & Pre-Flight:** Before any agent begins work on an established git project, it MUST run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` to perform all pre-flight routines (evaluating `ag-quota` velocity, auto-pulling/rebasing latest git changes, etc.) in a single step.
- **Auto-Commit & Push:** Whenever an agent concludes work involving code or documentation changes on a git repository, it MUST execute `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py -m "<message>" [--paths <files>]` to stage, commit, and immediately push commits (`git push`) to the remote repository. The agent writes the commit message itself (a specific subject line, plus a short body on *why* when useful); without `-m` the script falls back to a generic "Update <files>" summary. Use `--paths` to commit only this session's files. NEVER leave working tree changes uncommitted or unpushed at task conclusion.
- **Branch Protection & Staging Invariants (Daily Mini-Crossword)**: For `daily-mini-crossword`, all agents and developers MUST work and commit exclusively on the `working` branch. NEVER commit or push directly to `main`. The `main` branch autodeploys to production on Vercel (`crossword.mattmurphy.ca`) and is reserved strictly for official public releases.
- **Always Push, Never Ask (2026-10-20)**: Matt pre-approves every commit and push agents think is right, `main` included. Never hold a commit or push for his approval; commit and push as soon as work is done. Run the secret scan first. Only exception: daily-mini-crossword `main` (see above).
- **Make It Live by Default (2026-10-20)**: When Matt asked for a change and it's tested and very likely working, make it live without waiting (merge it where the live job/app runs from, install it, switch it on), then tell him "I made this live; want me to undo it?". Only wait for his approval first when the change is genuinely experimental or likely to fail. Why: a finished change left on a side branch behind an easy-to-miss "should I make it live?" question confused him when the old version kept running. The daily-mini-crossword `main` (public production) rule above still applies.

## Ubiquitous Git Tracking Directive
- **All Code & Configs in Git**: Practically all scripts, tools, configurations, automation modules, dotfiles, and codebases MUST reside inside a Git repository backed by a remote repository (always `--private` by default unless explicitly public).
- **Proactive Untracked File Detection**: Whenever an agent encounters, modifies, or inspects files or scripts that are NOT inside a Git worktree:
  - The agent MUST immediately notify Matt that the files are untracked.
  - The agent MUST assume Matt wants them tracked in a Git repository and either initialize/link a private repo or bring them into an appropriate repository structure.

