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
  habit_gate.py page-done            the page's Done button (via the Mac connector): record the step
                                     and print the note that wakes every thread holding a message
  habit_gate.py page                 build today's page from the current rung's card bank (prints the HTML path)
  habit_gate.py score [DATE] < doc   record a page's taps (its db doc JSON on stdin); may change rung
  habit_gate.py status

Question ladder (logic_rungs.json, Matt 2026-10-22): symbols first, then words -> symbols, predicates,
reading formulas, simple symbolizing, then mixed Unit 5. Moves up only once every card in the rung
has been right and the last page scored >= advance_at; a page under drop_below steps back one rung.
State: data/logic_rung.json.
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


RUNGS = HERE / "logic_rungs.json"


def load_rungs():
    return json.loads(RUNGS.read_text())


def read_rung():
    p = DATA_DIR / "logic_rung.json"
    r = json.loads(p.read_text()) if p.exists() else {}
    return {"rung": 0, "right": [], "missed": [], "scored": [], **r}


def write_rung(r):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "logic_rung.json").write_text(json.dumps(r, indent=2, ensure_ascii=False))


def pick_cards(rung, r, n):
    """Last page's misses first, then cards never answered right, then the rest."""
    bank = rung["cards"]
    order = ([c for c in bank if c["card_id"] in r["missed"]]
             + [c for c in bank if c["card_id"] not in r["missed"] and c["card_id"] not in r["right"]]
             + [c for c in bank if c["card_id"] in r["right"] and c["card_id"] not in r["missed"]])
    return order[:n]


def score(doc, day):
    """Record a page's taps (its db doc: reviews with card_id/correct); returns the rung state."""
    lad, r = load_rungs(), read_rung()
    if day in r["scored"]:
        return r
    reviews = [v for v in doc.get("reviews", []) if v.get("card_id") not in doc.get("skipped", [])]
    right = [v["card_id"] for v in reviews if v.get("correct")]
    missed = [v["card_id"] for v in reviews if not v.get("correct")]
    r["scored"] = (r["scored"] + [day])[-30:]
    if not reviews:
        write_rung(r)
        return r
    r["right"] = sorted(set(r["right"]) | set(right))
    r["missed"] = sorted(set(missed) - set(right))
    frac = len(right) / len(reviews)
    bank = {c["card_id"] for c in lad["rungs"][r["rung"]].get("cards", [])}
    if frac < lad["drop_below"] and r["rung"] > 0:
        r["rung"] -= 1
    elif frac >= lad["advance_at"] and bank <= set(r["right"]) and r["rung"] < len(lad["rungs"]) - 1:
        r["rung"] += 1
    r["last"] = {"date": day, "right": len(right), "of": len(reviews)}
    write_rung(r)
    return r


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
    rung = load_rungs()["rungs"][read_rung()["rung"]]
    publish = ('as an Artifact with capabilities {"db": {}, "mcp": {"servers": [{"server": "My Mac", '
               '"tools": ["practice_done"]}]}} (same flashcard layout as the morning check-in; '
               f"never hand-write the page; if the publish rejects the mcp part, publish with just {{\"db\": {{}}}}: "
               f"the Done button then falls back to a link). Then run `python3 {SCRIPT} url <artifact url>` so other threads "
               "reuse the same page.")
    if url:
        page = f"Today's practice page already exists: {url}. Give him that link."
    elif "cards" in rung:
        page = (f"Make today's practice page: run `python3 {SCRIPT} page` and publish the HTML it prints "
                + publish + " Don't add or change questions: the ladder picks them.")
    else:
        cards = DATA_DIR / "practice" / f"{t.date().isoformat()}.json"
        page = (f"Make today's practice page: {n} multiple-choice PHIL 120 questions (about {minutes} "
                "minutes of work) for his current logic unit (read the 'Logic' line in "
                "~/projects/ai-os/docs/SCHOOL.md for the unit and chapters). "
                f"{rung['brief']} 4 plausible options each. Write them as JSON to {cards} "
                '(a list of {"prompt", "key" (optional list, one symbol per line), "options", "correct_index", "answer", '
                f'"elaboration"}}), then run `python3 {HERE / "practice.py"} {cards}` and publish the HTML '
                "it prints " + publish)
    return (
        "HABIT GATE (Matt set this up himself on 2026-10-22: he earns Claude by doing today's logic "
        "study step first; don't ask him whether he wants to, just hand it over). "
        f"{page} Your reply is at most 3 short lines: the page link, then 'Tap Done on the page "
        "when finished (or reply 👍 / type skip).' Don't work on his message yet; it stays queued in this thread and you "
        "carry on with it once he's done. Exception: if his message is urgent (stop a running task, "
        "a deadline, something broken), handle it and mention the page once.")


def score_hint(t):
    """Tell the agent to feed today's taps to the question ladder."""
    day = t.date().isoformat()
    url = read_gate(day).get("url")
    if not url:
        return ""
    return (f"Quietly, first: read his taps with ArtifactData get on {url}, collection 'practice', "
            f"doc_id '{day}', and pipe that document's JSON into `python3 {SCRIPT} score {day}` "
            "(it moves the question ladder). Don't mention scores unless he asks.")


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
                "few words, then carry on with his earlier request in this thread, if any. " + score_hint(t))
    if kind == "reaction":
        return None
    hold_thread(payload.get("prompt", ""), t)
    return held_context(cfg, state, habit, t)


def hold_thread(prompt, t):
    """Remember which project thread is holding a message, so the page's Done button can wake it."""
    m = re.search(r'<thread ts="(cmsg_[A-Za-z0-9]+)"', prompt)
    if not m:
        return
    g = read_gate(t.date().isoformat())
    if m.group(1) not in g.setdefault("waiting", []):
        g["waiting"].append(m.group(1))
        write_gate(g)


def page_done(cfg, state, t):
    """Done tapped on the page: record the step; the note tells the coordinator which threads to wake."""
    g = read_gate(t.date().isoformat())
    minutes = finish(cfg, state, t, skipped=False) if g["status"] == "pending" else None
    threads = g.get("waiting", [])
    wake = (" ".join(f"Wake thread {th} (message_thread)." for th in threads) + " Each one's agent says "
            "'Unlocked' in a few words and carries on with the message it was holding. " + score_hint(t)
            if threads else "No thread is holding a message; nothing to wake.")
    note = (f"Matt tapped Done on today's logic practice page (habit gate step "
            f"{f'recorded, {minutes} min' if minutes is not None else 'already recorded'}). {wake}\n\nUrgent: no")
    return {"minutes": minutes, "threads": threads, "note": note}


def build_page(cfg, state, t):
    """Write today's cards from the current rung's bank and build the page; returns the HTML path."""
    import practice
    r = read_rung()
    rung = load_rungs()["rungs"][r["rung"]]
    habit = gate_cfg(cfg).get("habit")
    n = max(3, ladder.dose(cfg, state, habit)) if habit in state["active"] else 5
    cards = pick_cards(rung, r, n)
    day = t.date().isoformat()
    (DATA_DIR / "practice").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "practice" / f"{day}.json").write_text(json.dumps(cards, indent=1, ensure_ascii=False))
    out = DATA_DIR / "build" / f"practice-{day}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(practice.build(cards, day, "Logic practice: " + rung["name"].lower(),
                                  "PHIL 120 · Symbolic Logic"))
    return out


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "status"
    cfg = ladder.load_config()
    state = ladder.read_state(cfg, DATA_DIR)
    t = now()
    if cmd == "hook":
        try:
            payload = json.loads(sys.stdin.read() or "{}")
            ctx = hook(payload, cfg)
        except Exception as e:  # a broken gate must never block Claude
            print(f"habit_gate: {e}", file=sys.stderr)
            return 0
        try:  # missed morning check-in: a one-line nudge, never a hold
            if classify(payload.get("prompt", ""))[0] == "matt":
                import missed
                ctx = "\n\n".join(filter(None, [missed.nudge(), ctx])) or None
        except Exception as e:
            print(f"missed check-in nudge: {e}", file=sys.stderr)
        if ctx:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                                     "additionalContext": ctx}}))
    elif cmd in ("done", "skip"):
        print(f"recorded {finish(cfg, state, t, skipped=cmd == 'skip')} min")
    elif cmd == "page-done":
        print(json.dumps(page_done(cfg, state, t), ensure_ascii=False))
    elif cmd == "page":
        print(build_page(cfg, state, t))
    elif cmd == "score":
        day = argv[2] if len(argv) > 2 else t.date().isoformat()
        r = score(json.loads(sys.stdin.read() or "{}"), day)
        print(json.dumps({"rung": r["rung"], "name": load_rungs()["rungs"][r["rung"]]["name"],
                          "last": r.get("last")}, ensure_ascii=False))
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
