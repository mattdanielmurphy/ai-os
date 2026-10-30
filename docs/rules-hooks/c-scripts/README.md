# Angle C analysis scripts

Run from `~/projects/ai-os/tmp/rules-c/` (outputs land there, gitignored).

1. `metrics.py` parses the last ~11 days of `~/.claude/projects/*/*.jsonl` into `ev.pkl` (events, per-session context sizes, local_ → CLI id map).
2. `a_sends.py`: target thread size at the moment of each SendMessage.
3. `a_replies.py` → `turns.json`, then `a_reply_metrics.py` → `turns_d.json`: Matt-triggered turns, the reply he saw, his next message; lengths, asks, Actions lines, bare paths.
4. `a_tools.py` / `a_tools2.py`: tool-level checks (guard denials, rm, /tmp, .env, school paths, quiz menus).
5. `corpus.py` → `refine.py` → `cands.py`: Matt's own messages plus the agent turn before each, filtered for corrections.
