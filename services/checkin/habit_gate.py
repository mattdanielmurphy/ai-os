#!/usr/bin/env python3
"""Habit gate: Matt earns Claude by finishing today's habit step first.

Matt, 2026-10-22: "I'm addicted to Claude", so having to finish a step before using it is
"a fantastic incentive". He asked not to be asked; he just gets the logic questions.

Runs as a Claude Code UserPromptSubmit hook (Code tab and project threads on his Mac). It never
blocks a prompt: it adds context telling the agent to hand over today's logic practice page and
hold the request until Matt replies 👍 / "done" (or "skip"). Gentle by design, per the ladder:
  - only on the habit's days, after `after` (local time), until the step is recorded today
  - "skip" lets him through and records 0, so the ladder shrinks the dose instead of nagging
  - only Matt's own messages are gated; relays, agents, schedules and side-session events pass

Config: "gate" in ladder.json. State: data/gate.json (gitignored), one day at a time.

CLI (agents use these):
  habit_gate.py hook                 read the hook JSON on stdin, print hook JSON
  habit_gate.py done | skip          record today's step and unlock
  habit_gate.py url <artifact-url>   remember today's practice page so other threads reuse it
  habit_gate.py status
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ladder  # noqa: E402

DATA_DIR = Path(os.environ.get("HABIT_GATE_DATA", ladder.DATA_DIR))
SCRIPT = Path(__file__).resolve()

# Wakes and envelopes that aren't Matt typing to an agent.
NOT_MATT = ("<relay", "<cross-session-message", "<side-sessions-event", "<task-notification",
            "<ci-monitor-event", "<project_claude_message", "<coordinator-relay", "<scheduled")


def now():
    fake = os.environ.get("HABIT_GATE_NOW")  # tests: 2026-10-22T15:00
    return datetime.fromisoformat(fake) if fake else datetime.now()


def gate_cfg(cfg):
    return cfg.get("gate") or {}


def read_gate(today):
    p = DATA_DIR / "gate.json"
    g = json.loads(p.read_text()) if p.exists() else {}
    return g if g.get("date") == today else {"date": today, "status": "pending"}


def write_gate(g):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "gate.json").write_text(json.dumps(g, indent=2))


def classify(prompt):
    """('matt', text) for Matt's own message, ('reaction', prompt) for his reactions, else ('other', '')."""
    if "<wake" in prompt:
        if 'reason="reactions"' in prompt:
            return "reaction", prompt
        m = re.search(r'<message\b[^>]*trigger="true"[^>]*>(.*?)</message>', prompt, re.S)
        if 'reason="mention"' in prompt and m and 'from="human"' in m.group(0):
            return "matt", m.group(1)
        return "other", ""
    if any(tag in prompt for tag in NOT_MATT):
        return "other", ""
    return "matt", prompt


def due(cfg, state, t):
    """The habit key if the gate applies right now, else None."""
    g = gate_cfg(cfg)
    habit = g.get("habit")
    if not g.get("enabled") or habit not in cfg["habits"] or habit not in state["active"]:
        return None
    if not ladder.scheduled(cfg, habit, t.date()) or t.strftime("%H:%M") < g.get("after", "00:00"):
        return None
    today = t.date().isoformat()
    rec = next((r for r in ladder.read_history(DATA_DIR) if r["date"] == today), {})
    if habit in rec or read_gate(today)["status"] != "pending":
        return None
    return habit


def finish(cfg, state, t, skipped):
    habit = gate_cfg(cfg)["habit"]
    today = t.date().isoformat()
    minutes = 0 if skipped else ladder.dose(cfg, state, habit)
    ladder.append_record({"date": today, habit: minutes}, DATA_DIR)
    g = read_gate(today)
    g["status"] = "skipped" if skipped else "done"
    write_gate(g)
    return minutes


def held_context(cfg, state, habit, t):
    minutes = ladder.dose(cfg, state, habit)
    n = max(3, minutes)
    url = read_gate(t.date().isoformat()).get("url")
    if url:
        page = f"Today's practice page already exists: {url}. Give him that link."
    else:
        cards = DATA_DIR / "practice" / f"{t.date().isoformat()}.json"
        page = (f"Make today's practice page: {n} multiple-choice PHIL 120 questions (about {minutes} "
                "minutes of work) for his current logic unit (read the 'Logic' line in "
                "~/projects/ai-os/docs/SCHOOL.md for the unit and chapters). Mix symbolization and "
                f"quick-check questions, 4 plausible options each. Write them as JSON to {cards} "
                '(a list of {"prompt", "key" (optional list, one symbol per line), "options", "correct_index", "answer", '
                f'"elaboration"}}), then run `python3 {HERE / "practice.py"} {cards}` and publish the HTML '
                'it prints as an Artifact with capabilities {"db": {}} (same flashcard layout as the morning '
                "check-in; never hand-write the page). Then run "
                f"`python3 {SCRIPT} url <artifact url>` so other threads reuse the same page.")
    return (
        "HABIT GATE (Matt set this up himself on 2026-10-22: he earns Claude by doing today's logic "
        "study step first; don't ask him whether he wants to, just hand it over). "
        f"{page} Your reply is at most 3 short lines: the page link, then 'Reply 👍 when done "
        "(or type skip).' Don't work on his message yet; it stays queued in this thread and you "
        "carry on with it once he's done. Exception: if his message is urgent (stop a running task, "
        "a deadline, something broken), handle it and mention the page once.")


def hook(payload, cfg=None):
    cfg = cfg or ladder.load_config()
    state = ladder.read_state(cfg, DATA_DIR)
    t = now()
    kind, text = classify(payload.get("prompt", ""))
    if kind == "other":
        return None
    habit = due(cfg, state, t)
    if not habit:
        return None
    word = text.strip().lower().strip(".! ")
    if word == "skip":
        finish(cfg, state, t, skipped=True)
        return ("HABIT GATE: Matt skipped today's study step (recorded; the ladder may shrink tomorrow's "
                "dose). Say 'Unlocked' in a few words, no guilt, then carry on with his earlier request "
                "in this thread, if any.")
    if word in ("done", "👍") or (kind == "reaction" and "👍" in text):
        m = finish(cfg, state, t, skipped=False)
        return (f"HABIT GATE: Matt finished today's study step ({m} min, recorded). Say 'Unlocked' in a "
                "few words, then carry on with his earlier request in this thread, if any.")
    if kind == "reaction":
        return None
    return held_context(cfg, state, habit, t)


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "status"
    cfg = ladder.load_config()
    state = ladder.read_state(cfg, DATA_DIR)
    t = now()
    if cmd == "hook":
        try:
            ctx = hook(json.loads(sys.stdin.read() or "{}"), cfg)
        except Exception as e:  # a broken gate must never block Claude
            print(f"habit_gate: {e}", file=sys.stderr)
            return 0
        if ctx:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                                     "additionalContext": ctx}}))
    elif cmd in ("done", "skip"):
        print(f"recorded {finish(cfg, state, t, skipped=cmd == 'skip')} min")
    elif cmd == "url":
        g = read_gate(t.date().isoformat())
        g["url"] = argv[2]
        write_gate(g)
        print("saved")
    else:
        g = read_gate(t.date().isoformat())
        print(json.dumps({"due": due(cfg, state, t), **g}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
