# Claude weekly usage pace (2026-10-25)

## 12:58 CodexBar check + pace script

Asked (via coordinator): is CodexBar + its CLI installed; make a tiny command that prints Claude weekly usage and whether he's on pace, so the coordinator can pick Opus or Sonnet.

---

### CodexBar already installed

CodexBar 0.65.0 app plus `codexbar` CLI at `/opt/homebrew/bin/codexbar`, signed in to claude.ai (Max 5x). Nothing to install.

---

### Pace command

`python3 ~/projects/ai-os/scripts/claude_pace.py` (add `--json` for the coordinator). Reads `codexbar usage --provider claude --json`, compares weekly % used against even pace (time elapsed in the 7-day window) and prints OPUS / CAREFUL / SONNET.

- OPUS: at or under even pace. CAREFUL: up to 5 points over. SONNET: more than 5 over, or the 5-hour session window at 85%+.
- Exit codes 0/1/2, 3 on error, so scripts can branch on it.
- Even-pace math matched CodexBar's own "Expected 42%" on the first run.
- Thresholds are constants at the top of the script; not in the Tweaks panel (CLI, no feel knobs).
- Falls back to the brew path when PATH lacks it (launchd). Reads no .env or keys; CodexBar holds the claude.ai cookie.

Rejected: parsing ccusage logs (costs, not plan %), or re-deriving pace from scratch when CodexBar returns it.

Untested: behaviour when CodexBar's claude.ai cookie expires (should print ERROR, exit 3).

Undo: delete `scripts/claude_pace.py`.
