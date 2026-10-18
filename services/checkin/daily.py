#!/usr/bin/env python3
"""Daily morning check-in job: everything that doesn't need Claude.

The scheduled task `morning-checkin` (Claude desktop) does the three tool-only bits (read the page's db,
read Google Calendar, publish the Artifact) and calls this script for the rest:

  daily.py prepare --date D [--checkin F] [--events F]
      1. Record yesterday's page results (F = the ArtifactData file for checkins/<yesterday>) into the ladder,
         and apply its flashcard ratings to the FSRS deck. Both are idempotent.
      2. Plan today, start today's Sonnet reflection thread (Remote Control CLI in tmux), get its link.
      3. Build the page with real due cards and a fresh Cyanide & Happiness comic.
      Prints JSON: {"page": <html path>, "thread_url": ..., ...}
  daily.py send --date D [--force]
      iMessage Matt the page link via Photon (once per day unless --force).

Run with the assistant venv (needs `fsrs`): services/assistant/.venv/bin/python services/checkin/daily.py ...
"""
import argparse, base64, json, os, re, shlex, sqlite3, subprocess, sys, time, uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
import ladder  # noqa: E402

ARTIFACT_URL = "https://claude.ai/artifact/5CLZnpsQVxcFDP7bmALrNC"
CARDS_DB = Path(os.getenv("ASSISTANT_DB_PATH", Path.home() / ".hermes/assistant.db"))
PHOTON_ENV = Path.home() / "projects/daily-mini-crossword/.env"
IDENTITY = ROOT / "private/identity.md"
VAULT = Path.home() / "Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal"
TMUX = "checkin-reflection"
MAX_CARDS = 20


def _days(data_dir):
    p = Path(data_dir) / "days.json"
    return p, (json.loads(p.read_text()) if p.exists() else {})


def _save_day(data_dir, day, **fields):
    p, days = _days(data_dir)
    days.setdefault(day, {}).update(fields)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(days, indent=2))


# ---- 1. yesterday's results ---------------------------------------------

def load_checkin(path):
    """ArtifactData writes {"id", "data", "version", ...} or just the fields; return the fields or None."""
    if not path or not Path(path).exists():
        return None
    doc = json.loads(Path(path).read_text())
    return doc.get("data", doc) if isinstance(doc, dict) else None


def record_from_checkin(doc, planned, due_total):
    """Turn a page doc into ladder.py record values."""
    reviews = doc.get("reviews") or []
    values = {
        "breaths": int(doc.get("breaths") or 0),
        "gratitude": 1 if str(doc.get("gratitude") or "").strip() else 0,
        # No cards due that day counts as hitting the dose.
        "cards": len(reviews) if (reviews or due_total) else planned.get("cards", 0),
    }
    for k, v in (doc.get("extras") or {}).items():
        values[k] = v
    return values


def apply_reviews(doc, day, db_path=CARDS_DB):
    """Feed the page's ratings into the FSRS deck. Log ids are deterministic, so re-runs skip."""
    from services.assistant.spaced_repetition.engine import FSRSEngine
    eng, applied = FSRSEngine(), 0
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        for r in doc.get("reviews") or []:
            log_id = f"page-{day}-{r['card_id']}"
            if con.execute("SELECT 1 FROM fsrs_logs WHERE log_id = ?", (log_id,)).fetchone():
                continue
            row = con.execute("SELECT * FROM fsrs_cards WHERE card_id = ?", (r["card_id"],)).fetchone()
            if not row or r.get("rating") not in (1, 2, 3, 4):
                continue
            at = datetime.fromisoformat(r["at"].replace("Z", "+00:00")) if r.get("at") else datetime.now(timezone.utc)
            card, log = eng.review(dict(row), int(r["rating"]), at)
            con.execute(
                "UPDATE fsrs_cards SET stability=?, difficulty=?, reps=?, lapses=?, state=?, last_review=?, due_at=? WHERE card_id=?",
                (card["stability"], card["difficulty"], card["reps"], card["lapses"], card["state"],
                 card["last_review"].isoformat(), card["due_at"].isoformat(), r["card_id"]))
            con.execute("INSERT INTO fsrs_logs (log_id, card_id, rating, review_time, scheduled_days) VALUES (?,?,?,?,?)",
                        (log_id, r["card_id"], r["rating"], at.isoformat(), log["scheduled_days"]))
            applied += 1
        con.commit()
    finally:
        con.close()
    return applied


# ---- 2. today's inputs ----------------------------------------------------

def due_cards(db_path=CARDS_DB, limit=MAX_CARDS):
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(
            """SELECT card_id, prompt, answer, elaboration, options, correct_index FROM fsrs_cards
               WHERE due_at <= ? AND options IS NOT NULL AND trim(options) NOT IN ('', '[]')
               ORDER BY due_at, card_id LIMIT ?""",
            (datetime.now(timezone.utc).isoformat(), limit)).fetchall()
    finally:
        con.close()
    return [dict(r) for r in rows]


def fetch_comic(data_dir, day):
    """Latest C&H, or a random archive one if the latest was already shown. Embedded as a data: URI."""
    from services.assistant.briefing.comic import _fetch_comic_details, EXPLOSM_BASE_URL
    seen_p = Path(data_dir) / "seen_comics.json"
    seen = json.loads(seen_p.read_text()) if seen_p.exists() else []
    _, days = _days(data_dir)
    if days.get(day, {}).get("comic_slug"):  # same-day re-run keeps the same comic
        det = _fetch_comic_details(f"{EXPLOSM_BASE_URL}/comics/{days[day]['comic_slug']}")
    else:
        det = _fetch_comic_details(EXPLOSM_BASE_URL + "/comics/latest")
    if det["slug"] in seen and det.get("random_slug") and not days.get(day, {}).get("comic_slug"):
        det = _fetch_comic_details(f"{EXPLOSM_BASE_URL}/comics/{det['random_slug']}")
    req = Request(det["image_url"], headers={"User-Agent": "Mozilla/5.0", "Referer": EXPLOSM_BASE_URL})
    with urlopen(req, timeout=20) as resp:
        mime = resp.headers.get_content_type() or "image/png"
        img = resp.read(8_000_000)
    if det["slug"] not in seen:
        seen_p.write_text(json.dumps((seen + [det["slug"]])[-30:]))
    _save_day(data_dir, day, comic_slug=det["slug"])
    return {"src": f"data:{mime};base64," + base64.b64encode(img).decode(), "page": det["page_url"]}


def reflection_seed(plan, events, day):
    text = (HERE / "reflection_prompt.md").read_text().split("\n---\n", 1)[1].strip()
    d = date.fromisoformat(day)
    fields = {
        "dateline": d.strftime("%A, %B ") + str(d.day),
        "status": plan["status"],
        "streak": plan["streak"],
        "changes": " ".join(plan["changes"]) or "no changes today",
        "reflection_minutes": plan["doses"].get("reflection", 1),
        "events": "; ".join(f"{e['when']} {e['what']}" for e in events) or "nothing scheduled",
        "date": day,
    }
    for k, v in fields.items():
        text = text.replace("{" + k + "}", str(v))
    return text


def start_thread(seed, day, data_dir, timeout=90):
    """Start the Sonnet reflection thread as a Remote Control CLI session in tmux; return its claude:// link.

    Desktop-app sessions can't be started (or Remote-Control-linked) from an unattended scheduled run,
    so the thread is a CLI session. It lives until tomorrow's run replaces it.
    """
    _, days = _days(data_dir)
    if days.get(day, {}).get("thread_url"):
        return days[day]["thread_url"]
    subprocess.run(["tmux", "kill-session", "-t", TMUX], capture_output=True)
    seed_file = Path(data_dir) / f"reflection-{day}.md"
    seed_file.write_text(seed)
    ladder_cmds = [f"Bash(python3 {HERE}/ladder.py record:*)", "Bash(python3 ~/projects/ai-os/services/checkin/ladder.py record:*)"]
    cmd = " ".join(shlex.quote(x) for x in [
        "/opt/homebrew/bin/claude", "--remote-control", f"Morning reflection {day}", "--model", "sonnet",
        "--permission-mode", "acceptEdits", "--add-dir", str(VAULT),
        "--allowedTools", *ladder_cmds, "Bash(apple-reminders add:*)",
    ]) + f' -- "$(cat {shlex.quote(str(seed_file))})"'
    subprocess.run(["tmux", "new-session", "-d", "-s", TMUX, "-x", "220", "-y", "60", "-c", str(ROOT), cmd], check=True)
    end = time.time() + timeout
    while time.time() < end:
        time.sleep(3)
        pane = subprocess.run(["tmux", "capture-pane", "-p", "-J", "-t", TMUX, "-S", "-200"],
                              capture_output=True, text=True).stdout
        m = re.search(r"claude\.ai/code/(session_[A-Za-z0-9]+)", pane)
        if m:
            url = f"claude://code/{m.group(1)}"
            _save_day(data_dir, day, thread_url=url)
            return url
    raise SystemExit(f"reflection thread gave no session link within {timeout}s (tmux session {TMUX})")


def prepare(a):
    cfg = ladder.load_config()
    today = date.fromisoformat(a.date)
    yday = (today - timedelta(days=1)).isoformat()
    out = {"date": a.date}

    doc = load_checkin(a.checkin)
    if doc:
        state = ladder.read_state(cfg, a.data_dir)
        planned = state["plans"].get(yday, {}).get("doses", {})
        _, days = _days(a.data_dir)
        due_total = days.get(yday, {}).get("due_total", 1)
        values = record_from_checkin(doc, planned, due_total)
        ladder.append_record({"date": yday, **values}, a.data_dir)
        out["recorded"] = {"date": yday, **values}
        out["fsrs_applied"] = apply_reviews(doc, yday, a.cards_db)
    else:
        out["recorded"] = None

    state, plan = ladder.plan(cfg, ladder.read_state(cfg, a.data_dir), ladder.read_history(a.data_dir), today)
    ladder.write_state(state, a.data_dir)
    out["plan"] = {k: plan[k] for k in ("status", "streak", "doses", "changes")}

    events = json.loads(Path(a.events).read_text()) if a.events else []
    work = Path(a.data_dir) / "build"
    work.mkdir(parents=True, exist_ok=True)
    (work / "events.json").write_text(json.dumps(events))
    cards = due_cards(a.cards_db)
    (work / "cards.json").write_text(json.dumps(cards))
    try:
        (work / "comic.json").write_text(json.dumps(fetch_comic(a.data_dir, a.date)))
        comic_args = ["--comic", str(work / "comic.json")]
    except Exception as e:  # the fixture comic is better than no page
        out["comic_error"] = f"{type(e).__name__}: {e}"
        comic_args = []
    _save_day(a.data_dir, a.date, due_total=len(cards))
    out["cards"] = len(cards)

    out["thread_url"] = start_thread(reflection_seed(plan, events, a.date), a.date, a.data_dir)
    page = HERE / "morning-checkin.html"
    subprocess.run([sys.executable, str(HERE / "build.py"), "--date", a.date, "--thread-url", out["thread_url"],
                    "--cards", str(work / "cards.json"), "--events", str(work / "events.json"), *comic_args,
                    "--out", str(page), "--data-dir", a.data_dir], check=True, capture_output=True)
    out["page"] = str(page)
    print(json.dumps(out, indent=2))


# ---- 3. iMessage -----------------------------------------------------------

def _env(path):
    env = {}
    for line in Path(path).read_text().splitlines():
        m = re.match(r"\s*(?:export\s+)?([A-Z_]+)\s*=\s*(.*)\s*$", line)
        if m:
            env[m.group(1)] = m.group(2).strip().strip("'\"")
    return env


def _recipient():
    for line in IDENTITY.read_text().splitlines():
        if "phone" in line.lower():
            m = re.search(r"\+\d{10,15}", line)
            if m:
                return m.group(0)
    raise SystemExit("no +E164 phone number in identity.md")


def send(a):
    _, days = _days(a.data_dir)
    if days.get(a.date, {}).get("sent_at") and not a.force:
        print(json.dumps({"sent": False, "reason": "already sent today"}))
        return
    env = _env(PHOTON_ENV)
    addr = env["IMESSAGE_SERVER_ADDRESS"].rstrip("/")
    if not addr.startswith("http"):
        addr = "http://" + addr
    url = addr if addr.endswith("/send") else addr + "/send"
    body = json.dumps({"recipient": _recipient(), "message": ARTIFACT_URL}).encode()
    req = Request(url, data=body, method="POST",
                  headers={"Content-Type": "application/json", "Authorization": f"Bearer {env['IMESSAGE_TOKEN']}"})
    with urlopen(req, timeout=30) as resp:
        res = json.loads(resp.read() or b"{}")
    if res.get("error") or res.get("success") is False:
        raise SystemExit(f"Photon refused: {res.get('error')}")
    _save_day(a.data_dir, a.date, sent_at=datetime.now().isoformat(timespec="seconds"))
    print(json.dumps({"sent": True, "message": ARTIFACT_URL}))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", default=str(ladder.DATA_DIR))
    ap.add_argument("--cards-db", default=str(CARDS_DB))
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--date", default=date.today().isoformat())
    p.add_argument("--checkin", help="ArtifactData file for checkins/<yesterday>; missing = no page use")
    p.add_argument("--events", help='JSON list of {"when", "what"} for today')
    s = sub.add_parser("send")
    s.add_argument("--date", default=date.today().isoformat())
    s.add_argument("--force", action="store_true")
    a = ap.parse_args()
    prepare(a) if a.cmd == "prepare" else send(a)


if __name__ == "__main__":
    main()
