#!/usr/bin/env python3
"""Daily morning check-in job: everything that doesn't need Claude.

The scheduled task `morning-checkin` (Claude desktop) reads Google Calendar (a Claude tool) and calls this script:

  daily.py prepare --date D [--events F]
      Plan today (habit ladder), pick and shuffle today's due cards, find a fresh Cyanide & Happiness comic (and download its image),
      start today's check-in thread (Sonnet, Remote Control CLI in tmux) seeded from checkin_prompt.md.
      Prints JSON: {"thread_url": ..., "plan": ..., "cards": ...}
  daily.py send --date D [--force]
      iMessage Matt the thread link via Photon (once per day unless --force).
  daily.py finish --date D --breaths N --gratitude N [--answer CARD_ID=INDEX ...]
      Run by the thread itself once Matt has answered: grades the cards, applies the ratings to the FSRS deck
      (right = Good, wrong = Again; idempotent) and records breaths/gratitude/cards in the ladder.

Run with the assistant venv (needs `fsrs`): services/assistant/.venv/bin/python services/checkin/daily.py ...
"""
import argparse, json, os, random, re, shlex, sqlite3, subprocess, sys, time
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
import ladder  # noqa: E402

CARDS_DB = Path(os.getenv("ASSISTANT_DB_PATH", Path.home() / ".hermes/assistant.db"))
PHOTON_ENV = Path.home() / "projects/daily-mini-crossword/.env"
IDENTITY = ROOT / "private/identity.md"
VAULT = Path.home() / "Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal"
PY = ROOT / "services/assistant/.venv/bin/python"
TMUX = "checkin-thread"
MAX_CARDS = 20


def _days(data_dir):
    p = Path(data_dir) / "days.json"
    return p, (json.loads(p.read_text()) if p.exists() else {})


def _save_day(data_dir, day, **fields):
    p, days = _days(data_dir)
    days.setdefault(day, {}).update(fields)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(days, indent=2))


# ---- cards ----------------------------------------------------------------

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


def shuffle_card(card, day):
    """Shuffle a card's options (same order for a same-day re-run) and move correct_index with them."""
    opts = json.loads(card["options"]) if isinstance(card["options"], str) else list(card["options"])
    order = list(range(len(opts)))
    random.Random(f"{day}:{card['card_id']}").shuffle(order)
    return {**card, "options": [opts[i] for i in order], "correct_index": order.index(int(card["correct_index"]))}


def card_questions(cards):
    """AskUserQuestion payloads, one card per call, so each answer can be marked before the next card."""
    return [{"questions": [{"question": c["prompt"], "header": f"Card {i + 1} of {len(cards)}", "multiSelect": False,
                            "options": [{"label": o, "description": ""} for o in c["options"]]}]}
            for i, c in enumerate(cards)]


def grade(cards, answers):
    """answers: {card_id: picked index}. Returns [{card_id, correct, rating, answer}] for answered cards."""
    out = []
    for c in cards:
        if c["card_id"] not in answers:
            continue
        ok = answers[c["card_id"]] == c["correct_index"]
        out.append({"card_id": c["card_id"], "correct": ok, "rating": 3 if ok else 1,
                    "answer": c["answer"], "elaboration": c.get("elaboration") or ""})
    return out


def apply_reviews(reviews, day, db_path=CARDS_DB):
    """Feed ratings into the FSRS deck. Log ids are deterministic per day and card, so re-runs skip."""
    from services.assistant.spaced_repetition.engine import FSRSEngine
    eng, applied = FSRSEngine(), 0
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        for r in reviews:
            log_id = f"checkin-{day}-{r['card_id']}"
            if con.execute("SELECT 1 FROM fsrs_logs WHERE log_id = ?", (log_id,)).fetchone():
                continue
            row = con.execute("SELECT * FROM fsrs_cards WHERE card_id = ?", (r["card_id"],)).fetchone()
            if not row or r.get("rating") not in (1, 2, 3, 4):
                continue
            at = datetime.now(timezone.utc)
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


def thread_seed(plan, events, cards, comic, day, data_dir=ladder.DATA_DIR, cards_db=CARDS_DB, comic_image=None):
    text = (HERE / "checkin_prompt.md").read_text().split("\n---\n", 1)[1].strip()
    d = date.fromisoformat(day)
    doses = plan["doses"]
    # Non-default paths (tests) are passed through so the thread writes where prepare read.
    extra_l = f" --data-dir {data_dir}" if Path(data_dir) != ladder.DATA_DIR else ""
    extra = extra_l + (f" --cards-db {cards_db}" if Path(cards_db) != CARDS_DB else "")
    breaths = doses.get("breaths", 1)
    things = doses.get("gratitude", 1)
    if cards:
        batches = card_questions(cards)
        intro = (f"{len(cards)} card{'s' if len(cards) != 1 else ''}, one AskUserQuestion call each, in order. "
                 f"First, silently Read `{Path(data_dir) / 'build' / 'cards.json'}` for the answer key "
                 f"(each card's options and 0-based correct_index; never show it).")
        block = "\n".join(json.dumps(b, ensure_ascii=False) for b in batches)
    else:
        intro, block = "No cards are due today. Skip this step and record with no `--answer`.", ""
    fields = {
        "dateline": d.strftime("%A, %B ") + str(d.day),
        "status": plan["status"],
        "streak": plan["streak"],
        "changes": " ".join(plan["changes"]) or "no changes today",
        "breaths_gratitude_question": json.dumps({"questions": [
            {"question": f"Take {breaths} slow breath{'s' if breaths != 1 else ''}: in for 4, out for 6. Tap when done.",
             "header": "Breathe", "multiSelect": False,
             "options": [{"label": "Done", "description": f"{breaths} breaths"},
                         {"label": "Only some", "description": "Still counts"},
                         {"label": "Skip today", "description": "That's okay"}]},
            {"question": ("What's one thing you're grateful for this morning?" if things == 1
                          else f"What are {things} things you're grateful for this morning?")
                         + " Type it or dictate (pick Other), or say skip.",
             "header": "Gratitude", "multiSelect": False,
             "options": [{"label": "Skip today", "description": "That's okay"},
                         {"label": "I'll type it", "description": "Use Other below to dictate"}]},
        ]}, ensure_ascii=False),
        "breaths": breaths,
        "breaths_some": max(1, breaths - 1),
        "cards_intro": intro,
        "cards_block": block,
        "finish_cmd": f"{PY} {HERE}/daily.py{extra} finish --date {day}",
        "ladder_args": extra_l,
        "events": "; ".join(f"{e['when']} {e['what']}" for e in events) or "Nothing on the calendar today.",
        "reflection_minutes": doses.get("reflection", 1),
        "here": HERE,
        "vault": VAULT,
        "comic_url": comic or "https://explosm.net/comics/latest",
        "comic_step": (f'Show him the comic image: send `{comic_image}` with the SendUserFile tool '
                       f'(display "render", caption "Today\'s comic"). If that tool isn\'t available, skip '
                       f'this.' if comic_image else ""),
        "date": day,
    }
    for k, v in fields.items():
        text = text.replace("{" + k + "}", str(v))
    return text


def start_thread(seed, day, data_dir, timeout=90):
    """Start the check-in thread as a Remote Control CLI session in tmux; return its claude:// link.

    Desktop-app sessions can't be started (or Remote-Control-linked) from an unattended scheduled run,
    so the thread is a CLI session. It lives until tomorrow's run replaces it.
    """
    _, days = _days(data_dir)
    if days.get(day, {}).get("thread_url"):
        return days[day]["thread_url"]
    subprocess.run(["tmux", "kill-session", "-t", TMUX], capture_output=True)
    seed_file = Path(data_dir) / f"checkin-{day}.md"
    seed_file.write_text(seed)
    allowed = [f"Bash({PY} {HERE}/daily.py finish:*)", f"Bash(python3 {HERE}/ladder.py record:*)",
               "Bash(apple-reminders add:*)"]
    cmd = " ".join(shlex.quote(x) for x in [
        "/opt/homebrew/bin/claude", "--remote-control", f"Morning check-in {day}", "--model", "sonnet",
        # Bypass: Matt answers this thread from his phone; per-command prompts broke the flow (2026-10-17).
        "--permission-mode", "bypassPermissions", "--add-dir", str(VAULT), "--allowedTools", *allowed,
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
    raise SystemExit(f"check-in thread gave no session link within {timeout}s (tmux session {TMUX})")


def prepare(a):
    cfg = ladder.load_config()
    out = {"date": a.date}
    state, plan = ladder.plan(cfg, ladder.read_state(cfg, a.data_dir), ladder.read_history(a.data_dir),
                              date.fromisoformat(a.date))
    ladder.write_state(state, a.data_dir)
    out["plan"] = {k: plan[k] for k in ("status", "streak", "doses", "changes")}

    events = json.loads(Path(a.events).read_text()) if a.events else []
    due = due_cards(a.cards_db)
    cards = [shuffle_card(c, a.date) for c in due[:max(1, plan["doses"].get("cards", 1))]]
    work = Path(a.data_dir) / "build"
    work.mkdir(parents=True, exist_ok=True)
    (work / "cards.json").write_text(json.dumps({"date": a.date, "cards": cards}, ensure_ascii=False))
    _save_day(a.data_dir, a.date, due_total=len(due))
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

    seed = thread_seed(plan, events, cards, comic, a.date, a.data_dir, a.cards_db, image)
    out["thread_url"] = start_thread(seed, a.date, a.data_dir)
    print(json.dumps(out, indent=2))


def finish(a):
    work = json.loads((Path(a.data_dir) / "build" / "cards.json").read_text())
    if work.get("date") != a.date:
        raise SystemExit(f"build/cards.json is for {work.get('date')}, not {a.date}")
    answers = {}
    for kv in a.answer:
        cid, _, idx = kv.partition("=")
        answers[cid.strip()] = int(idx)
    results = grade(work["cards"], answers)
    applied = apply_reviews(results, a.date, a.cards_db)
    cfg = ladder.load_config()
    planned = ladder.read_state(cfg, a.data_dir)["plans"].get(a.date, {}).get("doses", {})
    # No cards due counts as hitting the dose.
    cards_done = len(results) if work["cards"] else planned.get("cards", 0)
    rec = {"date": a.date, "breaths": a.breaths, "gratitude": a.gratitude, "cards": cards_done}
    ladder.append_record(rec, a.data_dir)
    _save_day(a.data_dir, a.date, finished_at=datetime.now().isoformat(timespec="seconds"))
    print(json.dumps({"recorded": rec, "fsrs_applied": applied,
                      "cards": [{k: r[k] for k in ("card_id", "correct", "answer")} for r in results]},
                     indent=2, ensure_ascii=False))


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
    link = days.get(a.date, {}).get("thread_url")
    if not link:
        raise SystemExit(f"no thread link for {a.date}; run prepare first")
    body = json.dumps({"recipient": _recipient(), "message": link}).encode()
    req = Request(url, data=body, method="POST",
                  headers={"Content-Type": "application/json", "Authorization": f"Bearer {env['IMESSAGE_TOKEN']}"})
    with urlopen(req, timeout=30) as resp:
        res = json.loads(resp.read() or b"{}")
    if res.get("error") or res.get("success") is False:
        raise SystemExit(f"Photon refused: {res.get('error')}")
    _save_day(a.data_dir, a.date, sent_at=datetime.now().isoformat(timespec="seconds"))
    print(json.dumps({"sent": True, "message": link}))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", default=str(ladder.DATA_DIR))
    ap.add_argument("--cards-db", default=str(CARDS_DB))
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--date", default=date.today().isoformat())
    p.add_argument("--events", help='JSON list of {"when", "what"} for today')
    s = sub.add_parser("send")
    s.add_argument("--date", default=date.today().isoformat())
    s.add_argument("--force", action="store_true")
    f = sub.add_parser("finish")
    f.add_argument("--date", default=date.today().isoformat())
    f.add_argument("--breaths", type=int, required=True)
    f.add_argument("--gratitude", type=int, required=True, help="number of things named (0 = skipped)")
    f.add_argument("--answer", action="append", default=[], metavar="CARD_ID=INDEX")
    a = ap.parse_args()
    {"prepare": prepare, "send": send, "finish": finish}[a.cmd](a)


if __name__ == "__main__":
    main()
