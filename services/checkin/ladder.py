#!/usr/bin/env python3
"""Self-adjusting habit ladder for the morning check-in.

Atomic Habits rules, applied once per morning by `plan`:
  - Consistency first. A day counts as kept if any check-in step was done.
  - Growth: at most one change per `growth_every_days`, only after that many kept
    days in a row where the habit hit its dose. Changes alternate between raising
    one habit a level and (after `unlock_after_streak` kept days) adding a new step.
  - One missed day (red flag): undo the most recent growth and freeze growth.
  - Two or more missed days in a row (panic): every habit drops to its floor.
  - Two kept days in a row below a habit's dose: that dose is too big, step it down.
  - A habit with "days" (weekday numbers, Mon=0) is only planned on those days; other days never count
    for or against it. "when" (e.g. "afternoon") marks a habit done outside the morning page; the page
    skips it and the talk thread asks about it the next morning. "own_track" habits grow on their own
    weekly clock (one step after a week of hitting every scheduled dose), apart from the shared one.

State lives in data/ (gitignored) next to this file:
  history.jsonl  one merged record per day, e.g. {"date": "...", "breaths": 3, "cards": 2}
  state.json     current levels, active steps, change events, per-day planned doses

CLI:
  ladder.py plan [--date YYYY-MM-DD]          print today's plan as JSON (idempotent per day)
  ladder.py record --date D key=value ...     merge results for a day, e.g. breaths=3 reflection=2
  ladder.py status                            human summary
"""

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "ladder.json"
DATA_DIR = HERE / "data"


def load_config(path=CONFIG_PATH):
    return json.loads(Path(path).read_text())


def initial_state(cfg):
    return {
        "levels": {k: h["start"] for k, h in cfg["habits"].items()},
        "active": [k for k, h in cfg["habits"].items() if h["active"]],
        "events": [],
        "freeze_until": None,
        "penalized_through": None,
        "plans": {},
    }


def dose(cfg, state, habit):
    levels = cfg["habits"][habit]["levels"]
    return levels[min(state["levels"][habit], len(levels) - 1)]


def scheduled(cfg, habit, day):
    days = cfg["habits"][habit].get("days")
    return days is None or day.weekday() in days


def amount(cfg, habit, value):
    unit = cfg["habits"][habit]["unit"]
    return f"{value:g} {unit[:-1] if value == 1 and unit.endswith('s') else unit}"


def _d(s):
    return date.fromisoformat(s)


def _kept(rec):
    return bool(rec) and any(isinstance(v, (int, float)) and v > 0 for k, v in rec.items() if k != "date")


def _event(state, today, kind, habit, frm, to, reason):
    state["events"].append({"date": today.isoformat(), "kind": kind, "habit": habit,
                            "from": frm, "to": to, "reason": reason})


def _undo_last_growth(cfg, state, today):
    """Reverse the newest growth event that hasn't been undone. Returns a sentence or None."""
    undone = {e.get("undoes") for e in state["events"] if e.get("undoes") is not None}
    for i in range(len(state["events"]) - 1, -1, -1):
        e = state["events"][i]
        if e["kind"] not in ("up", "unlock") or i in undone:
            continue
        h = e["habit"]
        label = cfg["habits"][h]["label"]
        if e["kind"] == "up":
            state["levels"][h] = e["from"]
            msg = f"{label} back to {amount(cfg, h, dose(cfg, state, h))}"
        else:
            if h in state["active"]:
                state["active"].remove(h)
            msg = f"{label} paused for now"
        _event(state, today, "undo", h, e["to"], e["from"], "missed a day")
        state["events"][-1]["undoes"] = i
        return msg
    return None


def plan(cfg, state, history, today):
    """Return (state, plan) for `today`. Pure apart from mutating `state`."""
    key = today.isoformat()
    if key in state["plans"] and "plan" in state["plans"][key]:
        return state, state["plans"][key]["plan"]

    habits = cfg["habits"]
    past = {r["date"]: r for r in history if r["date"] < key}
    kept_days = sorted(d for d, r in past.items() if _kept(r))
    changes, status = [], "green"

    # Streak of kept days ending yesterday, and misses since the last kept day.
    streak = 0
    d = today - timedelta(days=1)
    while _kept(past.get(d.isoformat())):
        streak += 1
        d -= timedelta(days=1)
    missed = (today - _d(kept_days[-1])).days - 1 if kept_days else 0
    already = _d(state["penalized_through"]) if state["penalized_through"] else None
    freeze = timedelta(days=cfg["freeze_after_miss_days"])

    if missed >= 1 and (already is None or already < today - timedelta(days=1)):
        if missed >= 2:
            status = "panic"
            for h in state["active"]:
                if state["levels"][h] > 0:
                    _event(state, today, "floor", h, state["levels"][h], 0, f"missed {missed} days")
                    state["levels"][h] = 0
            changes.append(f"Missed {missed} days, so everything is back to the smallest version. Just show up today.")
        else:
            status = "red"
            undone = _undo_last_growth(cfg, state, today)
            changes.append("Missed yesterday. " + (undone + ", so today is easy." if undone else "Today stays easy."))
        state["freeze_until"] = (today + freeze).isoformat()
        state["penalized_through"] = (today - timedelta(days=1)).isoformat()
    elif missed >= 1:
        status = "panic" if missed >= 2 else "red"

    # Dose too big: two kept days in a row under the planned dose.
    if status == "green" and len(kept_days) >= 2:
        last2 = kept_days[-2:]
        for h in list(state["active"]):
            under = all(
                h in state["plans"].get(d, {}).get("doses", {})
                and past[d].get(h, 0) < state["plans"][d]["doses"][h]
                for d in last2
            )
            if under and state["levels"][h] > 0:
                frm = state["levels"][h]
                state["levels"][h] -= 1
                _event(state, today, "down", h, frm, state["levels"][h], "under dose two days running")
                changes.append(f"{habits[h]['label']} eased to {amount(cfg, h, dose(cfg, state, h))}. Smaller is fine.")

    # Growth: one change per window, only while green and not frozen.
    every = cfg["growth_every_days"]
    frozen = state["freeze_until"] and today < _d(state["freeze_until"])
    window = [(today - timedelta(days=i)).isoformat() for i in range(1, every + 1)]
    own = {h for h in habits if habits[h].get("own_track")}

    def hit_all(h):
        days = [d for d in window if scheduled(cfg, h, _d(d))
                and h in state["plans"].get(d, {}).get("doses", {h: None})]
        return bool(days) and all(
            past.get(d, {}).get(h, 0) >= state["plans"].get(d, {}).get("doses", {}).get(h, dose(cfg, state, h))
            for d in days)

    def since_change(h):
        dates = [_d(e["date"]) for e in state["events"] if e["habit"] == h]
        return (today - max(dates)).days if dates else 10 ** 6

    def can_grow(h):
        return state["levels"][h] < len(habits[h]["levels"]) - 1 and hit_all(h)

    last_change = max((_d(e["date"]) for e in state["events"] if e["habit"] not in own), default=None)
    if status == "green" and not frozen and not changes and streak >= every and (
        last_change is None or (today - last_change).days >= every
    ):
        locked = [h for h in cfg["unlock_order"] if h not in state["active"]]
        growths = [e for e in state["events"] if e["kind"] in ("up", "unlock") and e["habit"] not in own]
        want_unlock = locked and streak >= cfg["unlock_after_streak"] and (not growths or growths[-1]["kind"] == "up")
        candidates = sorted((h for h in state["active"] if h not in own and can_grow(h)), key=lambda h: -since_change(h))
        if want_unlock or (not candidates and locked and streak >= cfg["unlock_after_streak"]):
            h = locked[0]
            state["active"].append(h)
            state["levels"][h] = 0
            _event(state, today, "unlock", h, None, 0, f"{streak} days in a row")
            changes.append(f"New this week: {habits[h]['label'].lower()} ({amount(cfg, h, dose(cfg, state, h))}).")
        elif candidates:
            h = candidates[0]
            frm = state["levels"][h]
            state["levels"][h] += 1
            _event(state, today, "up", h, frm, state["levels"][h], f"{streak} days in a row")
            changes.append(f"{habits[h]['label']} goes up to {amount(cfg, h, dose(cfg, state, h))}.")

    # Own-track habits (e.g. the afternoon study block) grow on their own weekly clock: one step after a full
    # window of hitting the dose on every scheduled day. A missed check-in still undoes their last step.
    if status == "green" and not frozen and not any("eased" in c for c in changes):
        for h in sorted(own & set(state["active"])):
            if since_change(h) >= every and can_grow(h):
                frm = state["levels"][h]
                state["levels"][h] += 1
                _event(state, today, "up", h, frm, state["levels"][h], f"hit every {habits[h]['unit']} dose this week")
                changes.append(f"{habits[h]['label']} goes up to {amount(cfg, h, dose(cfg, state, h))}.")

    doses = {h: dose(cfg, state, h) for h in state["active"] if scheduled(cfg, h, today)}
    result = {
        "date": key,
        "status": status,
        "streak": streak,
        "missed": missed,
        "doses": doses,
        "steps": [{"habit": h, "label": habits[h]["label"], "dose": doses[h], "unit": habits[h]["unit"],
                   **({"when": habits[h]["when"]} if habits[h].get("when") else {})}
                  for h in habits if h in doses],
        "changes": changes,
    }
    state["plans"][key] = {"doses": doses, "plan": result}
    return state, result


# ---- storage -------------------------------------------------------------

def read_history(data_dir=DATA_DIR):
    p = Path(data_dir) / "history.jsonl"
    if not p.exists():
        return []
    merged = {}
    for line in p.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            merged.setdefault(r["date"], {}).update(r)
    return [merged[d] for d in sorted(merged)]


def append_record(rec, data_dir=DATA_DIR):
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    with open(Path(data_dir) / "history.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")


def read_state(cfg, data_dir=DATA_DIR):
    p = Path(data_dir) / "state.json"
    if not p.exists():
        return initial_state(cfg)
    state = json.loads(p.read_text())
    for k, h in cfg["habits"].items():  # habits added to the config later
        state["levels"].setdefault(k, h["start"])
        if h["active"] and k not in state["active"] and k not in cfg["unlock_order"]:
            state["active"].append(k)
    return state


def write_state(state, data_dir=DATA_DIR):
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    (Path(data_dir) / "state.json").write_text(json.dumps(state, indent=2))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", default=str(DATA_DIR))
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--date", default=date.today().isoformat())
    r = sub.add_parser("record")
    r.add_argument("--date", default=date.today().isoformat())
    r.add_argument("values", nargs="+", help="habit=number, e.g. breaths=3")
    sub.add_parser("status")
    a = ap.parse_args(argv)

    cfg = load_config()
    if a.cmd == "record":
        rec = {"date": a.date}
        for kv in a.values:
            k, v = kv.split("=", 1)
            if k not in cfg["habits"]:
                sys.exit(f"unknown habit: {k}")
            rec[k] = float(v) if "." in v else int(v)
        append_record(rec, a.data_dir)
        print(json.dumps(rec))
        return
    state = read_state(cfg, a.data_dir)
    if a.cmd == "plan":
        state, result = plan(cfg, state, read_history(a.data_dir), _d(a.date))
        write_state(state, a.data_dir)
        print(json.dumps(result, indent=2))
    else:
        for h in state["active"]:
            print(f"{cfg['habits'][h]['label']}: {amount(cfg, h, dose(cfg, state, h))}")
        for e in state["events"][-5:]:
            print(f"  {e['date']} {e['kind']} {e['habit']} ({e['reason']})")


if __name__ == "__main__":
    main()
