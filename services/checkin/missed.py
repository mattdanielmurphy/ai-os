#!/usr/bin/env python3
"""Missed check-ins: notice them and step in (Matt, 2026-10-25: he stopped doing them and nothing noticed).

Two problems this fixes:
  - His iPhone Shortcut keeps only the LAST link the check-in sender texts him (pending_claude.txt), and the daily
    crossword comes from the same Photon sender at 9:00. When he wakes after 9 the crossword wins. So once the
    crossword has gone out, `tick` re-sends the check-in links if he hasn't started, which puts them last again.
  - Nobody noticed a string of missed days. `streak` counts them; the re-send says how many, and the first Claude
    prompt of the day (habit_gate.py hook) gets a one-line nudge with the check-in link. Neither holds anything up.

A day counts as done if the chat started (the Mac connector's checkin_today calls `missed.py started`) or the
page's results reached history.jsonl (ingested the next morning). No bed or wake reminders, ever: the re-send only
goes out once the crossword has, and it's the check-in links, not an alarm.

  missed.py tick       launchd, every 10 min: re-send after the crossword if not started (once a day)
  missed.py started    the check-in chat started today (Mac connector)
  missed.py status     JSON: today's state and the missed streak

Config: "watch" in ladder.json. State: data/days.json (sent_at, started_at, resent_at, nudged_at per day).
"""
import json, os, sys
from datetime import date, datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ladder  # noqa: E402
import daily  # noqa: E402

DATA_DIR = Path(os.environ.get("CHECKIN_DATA", ladder.DATA_DIR))
PAGE_KEYS = ("breaths", "gratitude", "cards", "reflection")


def now():
    fake = os.environ.get("CHECKIN_NOW")  # tests: 2026-10-25T09:10
    return datetime.fromisoformat(fake) if fake else datetime.now()


def cfg_watch(cfg=None):
    w = (cfg or ladder.load_config()).get("watch") or {}
    return {"enabled": True, "crossword_at": "09:00", "resend_after_min": 5, "nudge_until": "17:00", **w}


def done(day, days, history):
    rec = history.get(day, {})
    return bool(days.get(day, {}).get("started_at")) or any(k in rec for k in PAGE_KEYS)


def streak(today, days=None, history=None):
    """Missed check-ins in a row before today (only days whose links were sent count)."""
    days = days if days is not None else daily._days(DATA_DIR)[1]
    history = history if history is not None else {r["date"]: r for r in ladder.read_history(DATA_DIR)}
    n, d = 0, date.fromisoformat(today) - timedelta(days=1)
    while d.isoformat() in days and days[d.isoformat()].get("sent_at"):
        if done(d.isoformat(), days, history):
            break
        n, d = n + 1, d - timedelta(days=1)
    return n


def waiting(t, days=None):
    """True if today's links went out and the check-in hasn't started."""
    today = t.date().isoformat()
    days = days if days is not None else daily._days(DATA_DIR)[1]
    history = {r["date"]: r for r in ladder.read_history(DATA_DIR)}
    return bool(days.get(today, {}).get("sent_at")) and not done(today, days, history)


def resend_message(n):
    lines = ["Your morning check-in is still waiting. It takes about five minutes."]
    if n:
        lines.append(f"You've missed {n} day{'s' if n != 1 else ''} in a row, so today's is a small one. No guilt.")
    return "\n".join(lines) + f"\n{daily.CHAT_URL}\n{daily.ARTIFACT_URL}"


def tick(t=None, send=None):
    t = t or now()
    w = cfg_watch()
    today = t.date().isoformat()
    _, days = daily._days(DATA_DIR)
    day = days.get(today, {})
    if not w["enabled"] or not waiting(t, days) or day.get("resent_at"):
        return {"resent": False}
    h, m = map(int, w["crossword_at"].split(":"))
    due = t.replace(hour=h, minute=m, second=0, microsecond=0) + timedelta(minutes=w["resend_after_min"])
    if t < due or datetime.fromisoformat(day["sent_at"]) >= due:  # crossword not out yet, or ours already came after
        return {"resent": False}
    msg = resend_message(streak(today, days))
    (send or photon_send)(msg)
    daily._save_day(DATA_DIR, today, resent_at=t.isoformat(timespec="seconds"))
    return {"resent": True, "message": msg}


def photon_send(message):
    env = daily._env(daily.PHOTON_ENV)
    addr = env["IMESSAGE_SERVER_ADDRESS"].rstrip("/")
    addr = addr if addr.startswith("http") else "http://" + addr
    url = addr if addr.endswith("/send") else addr + "/send"
    body = json.dumps({"recipient": daily._recipient(), "message": message}).encode()
    req = daily.Request(url, data=body, method="POST", headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {env['IMESSAGE_TOKEN']}"})
    with daily.urlopen(req, timeout=30) as resp:
        res = json.loads(resp.read() or b"{}")
    if res.get("error") or res.get("success") is False:
        raise SystemExit(f"Photon refused: {res.get('error')}")


def nudge(t=None):
    """Context for Matt's first Claude prompt while today's check-in waits (once a day), else None."""
    t = t or now()
    w = cfg_watch()
    today = t.date().isoformat()
    _, days = daily._days(DATA_DIR)
    if (not w["enabled"] or t.strftime("%H:%M") >= w["nudge_until"] or not waiting(t, days)
            or days[today].get("nudged_at")):
        return None
    daily._save_day(DATA_DIR, today, nudged_at=t.isoformat(timespec="seconds"))
    n = streak(today, days)
    missed = f" He has missed {n} day{'s' if n != 1 else ''} in a row before today." if n else ""
    return ("CHECK-IN NUDGE (Matt asked for missed check-ins to be noticed, 2026-10-25): today's morning check-in "
            f"hasn't started yet.{missed} Start your reply with one short, warm line saying it's still waiting, with "
            f"this link: [Start the check-in]({daily.CHAT_URL}) (the page is {daily.ARTIFACT_URL}). No guilt, no "
            "lecture, and never suggest a bedtime or alarm. Then handle his message normally; don't hold it.")


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "status"
    t = now()
    today = t.date().isoformat()
    if cmd == "tick":
        print(json.dumps(tick(t)))
    elif cmd == "started":
        if not daily._days(DATA_DIR)[1].get(today, {}).get("started_at"):
            daily._save_day(DATA_DIR, today, started_at=t.isoformat(timespec="seconds"))
        print("ok")
    else:
        _, days = daily._days(DATA_DIR)
        print(json.dumps({"today": days.get(today, {}), "waiting": waiting(t, days), "missed_in_a_row": streak(today, days)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
