---
name: ai-os-auto-commit
description: Commit and push in ai-os via scripts/auto_commit.py with an agent-written message, a secret-audit gate and optional --paths scoping.
version: 2.0.0
metadata:
  hermes:
    tags: [ai-os, git, commit, automation]
---

# AI-OS Auto-Commit

`scripts/auto_commit.py` is the standard commit + push path in `~/projects/ai-os`.
You (the agent) write the commit message; the script handles staging, the secret gate and the push.

## Usage

```bash
cd ~/projects/ai-os
python3 scripts/auto_commit.py -m "Fix X: short specific subject" --paths path/one path/two
```

- `-m/--message`: your commit message. Write a specific subject line (what changed); add a blank line
  and a short body when the *why* isn't obvious. Multi-line messages are fine.
- `--paths`: stage and commit only these paths. Use it whenever other sessions may have left
  unrelated dirty files. Without it the script runs `git add .`.
- `--result-path`: optional JSON status file.

## What the script does

1. Moves in-progress `.devtool/features/*.md` tasks to `status: "review"`
2. Stages `--paths` (or everything)
3. Runs the secret audit gate; on a hit it unstages, aborts and exits non-zero
4. Commits with your `-m` message, or falls back to `Update <first 3 staged files> and N other file(s)`
5. Pushes (`git push`; detached HEAD pushes `HEAD:main`)

## Notes

- The fallback message is a last resort for unattended callers (`housekeep.py`, `postflight_async.py`).
  Agents should always pass `-m`.
- No LLM or proxy is involved any more (the LiteLLM step was removed on 2026-10-17).
