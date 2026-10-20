#!/usr/bin/env python3
"""Daily morning check-in job: everything that doesn't need Claude.

Two stages each morning: a page (Artifact: breaths, gratitude, flashcards; no model) whose last button opens a
talk thread (Sonnet, Remote Control CLI in tmux: how he feels, the day ahead, then the comic as the reward).

The scheduled task `morning-checkin` (Claude desktop) does the Claude-only bits (read yesterday's page doc and
Google Calendar, publish the page) and calls this script for the rest:

  daily.py prepare --date D [--checkin F] [--events F]
      1. Record yesterday's page results (F = the ArtifactData file for checkins/<yesterday>) into the ladder,
         apply its flashcard ratings to the FSRS deck and log its gratitude to Obsidian. All idempotent.
      2. Plan today, pick a fresh Cyanide & Happiness comic (and download its image), start today's talk thread
         with checkin_prompt.md as a hidden system prompt.
      3. Build the page (morning-checkin.html) with today's due cards.
      Prints JSON: {"page": ..., "thread_url": ..., "plan": ..., "cards": ...}
  daily.py send --date D [--force]
      iMessage Matt the thread link and the page link in one message via Photon (once per day unless --force);
      his iPhone Shortcut opens both in turn, so the page sits on top of the thread.

Run with the assistant venv (needs `fsrs`): services/assistant/.venv/bin/python services/checkin/daily.py ...
"""
import argparse, json, os, random, re, shlex, sqlite3, subprocess, sys, time
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
TMUX = "checkin-thread"
MAX_CARDS = 20
# Only school decks go in the check-in (Matt, 2026-10-20: no drums/music-theory/AI trivia). Card id prefix = subject.
SCHOOL_SUBJECTS = ("forallx", "cmput174", "music102")
KICKOFF = f"Morning check-in: {ARTIFACT_URL}"  # the only visible first message; the instructions are a hidden system prompt


def _days(data_dir):
    p = Path(data_dir) / "days.json"
    return p, (json.loads(p.read_text()) if p.exists() else {})


def _save_day(data_dir, day, **fields):
    p, days = _days(data_dir)
    days.setdefault(day, {}).update(fields)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(days, indent=2))


# ---- cards ----------------------------------------------------------------

def subject(card_id):
    """Deck subject from the card id prefix: forallx_ch01_q02 → forallx, music_cello_01 → music."""
    return card_id.split("_", 1)[0]


def mix_subjects(cards, day):
    """Interleave subjects so a short session covers all of them: one card per subject in turn, most overdue first
    within a subject. The subject that leads rotates by day, so no deck always gets the first slot."""
    groups = {}
    for c in cards:  # cards arrive most-overdue first
        groups.setdefault(subject(c["card_id"]), []).append(c)
    names = sorted(groups)
    if not names:
        return []
    k = date.fromisoformat(day).toordinal() % len(names)
    names = names[k:] + names[:k]
    out = []
    while any(groups.values()):
        for n in names:
            if groups[n]:
                out.append(groups[n].pop(0))
    return out


def due_cards(db_path=CARDS_DB, limit=MAX_CARDS, day=None):
    """Today's due cards (up to limit), mixed across subjects. Without the mix the most-overdue deck (logic, whose
    learning-step cards fall due again within minutes) filled every slot (Matt, 2026-10-20)."""
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(
            """SELECT card_id, prompt, answer, elaboration, options, correct_index FROM fsrs_cards
               WHERE due_at <= ? AND options IS NOT NULL AND trim(options) NOT IN ('', '[]')
               ORDER BY due_at, card_id""",
            (datetime.now(timezone.utc).isoformat(),)).fetchall()
    finally:
        con.close()
    rows = [dict(r) for r in rows if subject(r["card_id"]) in SCHOOL_SUBJECTS]
    return mix_subjects(rows, day or date.today().isoformat())[:limit]


def load_checkin(path):
    """ArtifactData writes {"id", "data", "version", ...} or just the fields; return the fields or None."""
    if not path or not Path(path).exists():
        return None
    doc = json.loads(Path(path).read_text())
    return doc.get("data", doc) if isinstance(doc, dict) else None


def record_from_checkin(doc, planned, due_total):
    """Turn a page doc into ladder record values."""
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
    """Feed the page's Again/Hard/Good/Easy ratings into the FSRS deck. Log ids are deterministic, so re-runs skip."""
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


def log_gratitude(doc, day, vault=VAULT):
    """Append the page's gratitude text to that day's Obsidian habit log, once."""
    text = str(doc.get("gratitude") or "").strip()
    if not text:
        return False
    log = Path(vault) / "habits/logs" / f"{day}.md"
    old = log.read_text() if log.exists() else ""
    line = f"- Grateful for: {' '.join(text.split())}"
    if line in old:
        return False
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(old + ("" if not old or old.endswith("\n") else "\n") + ("\n## Gratitude\n" if "## Gratitude" not in old else "") + line + "\n")
    return True


# ---- today's inputs ---------------------------------------------------------

def comic_url(data_dir, day):
    """Latest C&H page, or a random archive one if the latest was already shown."""
    from services.assistant.briefing.comic import _fetch_comic_details, EXPLOSM_BASE_URL
    _, days = _days(data_dir)
    if days.get(day, {}).get("comic_url"):  # same-day re-run keeps the same comic
        return days[day]["comic_url"]
    seen_p = Path(data_dir) / "seen_comics.json"
    seen = json.loads(seen_p.read_text()) if seen_p.exists() else []
    det = _fetch_comic_details(EXPLOSM_BASE_URL + "/comics/latest")
    if det["slug"] in seen and det.get("random_slug"):
        det = _fetch_comic_details(f"{EXPLOSM_BASE_URL}/comics/{det['random_slug']}")
    seen_p.write_text(json.dumps((seen + [det["slug"]])[-30:]))
    _save_day(data_dir, day, comic_url=det["page_url"], comic_image_url=det["image_url"])
    return det["page_url"]


def comic_image(data_dir, day):
    """Download today's comic image next to the day's data so the thread can show it; None if unavailable."""
    _, days = _days(data_dir)
    src = days.get(day, {}).get("comic_image_url")
    if not src:
        return None
    out = Path(data_dir) / f"comic-{day}{Path(src.split('?')[0]).suffix or '.png'}"
    if not out.exists():
        req = Request(src, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://explosm.net"})
        with urlopen(req, timeout=20) as resp:
            out.write_bytes(resp.read(10_000_000))
    return out


def recent_notes(day, vault=VAULT, days=4, limit=3000):
    """The last few days' Obsidian habit logs (before `day`), newest first, so the thread can ask about something live."""
    d, out = date.fromisoformat(day), []
    for i in range(1, days + 1):
        f = Path(vault) / "habits/logs" / f"{(d - timedelta(days=i)).isoformat()}.md"
        if f.exists():
            out.append(f"[{f.stem}]\n{f.read_text().strip()}")
    text = "\n\n".join(out)
    return (text[:limit] + "…") if len(text) > limit else (text or "(none yet)")


def thread_seed(plan, events, comic, day, data_dir=ladder.DATA_DIR, comic_image=None):
    """The talk thread's hidden system prompt, from checkin_prompt.md."""
    text = (HERE / "checkin_prompt.md").read_text().split("\n---\n", 1)[1].strip()
    d = date.fromisoformat(day)
    # A non-default data dir (tests) is passed through so the thread records where prepare read.
    extra_l = f" --data-dir {data_dir}" if Path(data_dir) != ladder.DATA_DIR else ""
    fields = {
        "dateline": d.strftime("%A, %B ") + str(d.day),
        "status": plan["status"],
        "streak": plan["streak"],
        "changes": " ".join(plan["changes"]) or "no changes today",
        "events": "; ".join(f"{e['when']} {e['what']}" for e in events) or "nothing on the calendar today",
        "recent_notes": recent_notes(day),
        "reflection_minutes": plan["doses"].get("reflection", 1),
        "here": HERE,
        "ladder_args": extra_l,
        "vault": VAULT,
        "comic_url": comic or "https://explosm.net/comics/latest",
        "comic_step": (f'send `{comic_image}` with the SendUserFile tool (display "render", caption "Today\'s comic"). '
                       f'If that tool isn\'t available, skip the image.' if comic_image else ""),
        "date": day,
    }
    for k, v in fields.items():
        text = text.replace("{" + k + "}", str(v))
    return text


def start_thread(seed, day, data_dir, timeout=90):
    """Start the check-in thread as a Remote Control CLI session in tmux; return its claude:// link.

    Desktop-app sessions can't be started (or Remote-Control-linked) from an unattended scheduled run,
    so the thread is a CLI session. It lives until tomorrow's run replaces it. The instructions go in as an
    appended system prompt, so the thread opens with just KICKOFF (today's page link) and Claude's first question.
    The page opens in the app's viewer over the thread; closing it lands back here.
    """
    _, days = _days(data_dir)
    if days.get(day, {}).get("thread_url"):
        return days[day]["thread_url"]
    subprocess.run(["tmux", "kill-session", "-t", TMUX], capture_output=True)
    seed_file = Path(data_dir) / f"checkin-{day}.md"
    seed_file.write_text(seed)
    allowed = [f"Bash(python3 {HERE}/ladder.py record:*)", "Bash(apple-reminders add:*)"]
    cmd = " ".join(shlex.quote(x) for x in [
        "/opt/homebrew/bin/claude", "--remote-control", f"Morning check-in {day}", "--model", "sonnet",
        # Bypass: Matt answers this thread from his phone; per-command prompts broke the flow (2026-10-17).
        "--permission-mode", "bypassPermissions", "--add-dir", str(VAULT), "--allowedTools", *allowed,
    ]) + f' --append-system-prompt "$(cat {shlex.quote(str(seed_file))})" -- {shlex.quote(KICKOFF)}'
    subprocess.run(["tmux", "new-session", "-d", "-s", TMUX, "-x", "220", "-y", "60", "-c", str(ROOT), cmd], check=True)
    end = time.time() + timeout
    while time.time() < end:
        time.sleep(3)
        pane = subprocess.run(["tmux", "capture-pane", "-p", "-J", "-t", TMUX, "-S", "-200"],
                              capture_output=True, text=True).stdout
        m = re.search(r"claude\.ai/code/(session_[A-Za-z0-9]+)", pane)
        if m:
            url = f"claude://code/{m.group(1)}"
            _save_day(data_dir, day, thread_url=url, session_id=m.group(1))
            return url
    raise SystemExit(f"check-in thread gave no session link within {timeout}s (tmux session {TMUX})")


def ingest(path, day, data_dir, cards_db=CARDS_DB, vault=VAULT):
    """Record a day's page results (ladder, FSRS deck, gratitude log). Returns a summary, or None if no doc."""
    doc = load_checkin(path)
    if not doc:
        return None
    cfg = ladder.load_config()
    planned = ladder.read_state(cfg, data_dir)["plans"].get(day, {}).get("doses", {})
    _, days = _days(data_dir)
    values = record_from_checkin(doc, planned, days.get(day, {}).get("due_total", 1))
    ladder.append_record({"date": day, **values}, data_dir)
    return {"date": day, **values, "fsrs_applied": apply_reviews(doc, day, cards_db),
            "gratitude_logged": log_gratitude(doc, day, vault)}


def prepare(a):
    cfg = ladder.load_config()
    today = date.fromisoformat(a.date)
    out = {"date": a.date}
    out["recorded"] = ingest(a.checkin, (today - timedelta(days=1)).isoformat(), a.data_dir, a.cards_db)

    state, plan = ladder.plan(cfg, ladder.read_state(cfg, a.data_dir), ladder.read_history(a.data_dir), today)
    ladder.write_state(state, a.data_dir)
    out["plan"] = {k: plan[k] for k in ("status", "streak", "doses", "changes")}

    events = json.loads(Path(a.events).read_text()) if a.events else []
    cards = due_cards(a.cards_db, day=a.date)
    work = Path(a.data_dir) / "build"
    work.mkdir(parents=True, exist_ok=True)
    (work / "cards.json").write_text(json.dumps(cards, ensure_ascii=False))
    _save_day(a.data_dir, a.date, due_total=len(cards))
    out["cards"] = len(cards)
    try:
        comic = comic_url(a.data_dir, a.date)
    except Exception as e:  # the latest-comic link is better than none
        out["comic_error"] = f"{type(e).__name__}: {e}"
        comic = None
    try:
        image = comic_image(a.data_dir, a.date)
    except Exception as e:  # the thread falls back to the link
        out["comic_image_error"] = f"{type(e).__name__}: {e}"
        image = None

    out["thread_url"] = start_thread(thread_seed(plan, events, comic, a.date, a.data_dir, image), a.date, a.data_dir)
    page = Path(a.out) if a.out else HERE / "morning-checkin.html"
    subprocess.run([sys.executable, str(HERE / "build.py"), "--date", a.date,
                    "--cards", str(work / "cards.json"), "--out", str(page), "--data-dir", a.data_dir],
                   check=True, capture_output=True)
    out["page"] = str(page)
    print(json.dumps(out, indent=2))


# ---- iMessage -----------------------------------------------------------

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
    thread = days.get(a.date, {}).get("thread_url")
    if not thread:
        raise SystemExit(f"no thread link for {a.date}; run prepare first")
    # One message, thread link first, then the page: Matt's iPhone Shortcut opens each URL in turn, so the page
    # opens on top of the thread and closing it lands him in the chat. (A page can't link into the app itself:
    # claude:// does nothing there and https opens Safari; 2026-10-19.)
    message = f"{thread}\n{ARTIFACT_URL}"
    body = json.dumps({"recipient": _recipient(), "message": message}).encode()
    req = Request(url, data=body, method="POST",
                  headers={"Content-Type": "application/json", "Authorization": f"Bearer {env['IMESSAGE_TOKEN']}"})
    with urlopen(req, timeout=30) as resp:
        res = json.loads(resp.read() or b"{}")
    if res.get("error") or res.get("success") is False:
        raise SystemExit(f"Photon refused: {res.get('error')}")
    _save_day(a.data_dir, a.date, sent_at=datetime.now().isoformat(timespec="seconds"))
    print(json.dumps({"sent": True, "message": message}))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", default=str(ladder.DATA_DIR))
    ap.add_argument("--cards-db", default=str(CARDS_DB))
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--date", default=date.today().isoformat())
    p.add_argument("--checkin", help="ArtifactData file for checkins/<yesterday>; missing = page not used")
    p.add_argument("--events", help='JSON list of {"when", "what"} for today')
    p.add_argument("--out", help="page path (default: morning-checkin.html here)")
    s = sub.add_parser("send")
    s.add_argument("--date", default=date.today().isoformat())
    s.add_argument("--force", action="store_true")
    a = ap.parse_args()
    {"prepare": prepare, "send": send}[a.cmd](a)


if __name__ == "__main__":
    main()
