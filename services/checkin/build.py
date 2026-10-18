#!/usr/bin/env python3
"""Build the morning check-in page from template.html.

Usage: build.py [--date YYYY-MM-DD] [--thread-url URL] [--cards F] [--comic F] [--events F] [--out morning-checkin.html]
Today's doses come from ladder.py (habit ladder). Without --cards/--comic the fixtures (cards.json, comic.png) are used.
--comic takes a JSON file {"src": <image url or data: URI>, "page": <explosm page url>}.
--events takes a JSON list of {"when": "9:00 AM", "what": "Dentist"}.
"""
import argparse, base64, json
from datetime import date
from pathlib import Path

import ladder

HERE = Path(__file__).resolve().parent

ap = argparse.ArgumentParser()
ap.add_argument("--date", default=date.today().isoformat())
ap.add_argument("--thread-url", default="", help="claude:// link to today's Sonnet reflection thread")
ap.add_argument("--cards", default=str(HERE / "cards.json"))
ap.add_argument("--comic", default="")
ap.add_argument("--events", default="")
ap.add_argument("--out", default=str(HERE / "morning-checkin.html"))
ap.add_argument("--data-dir", default=str(ladder.DATA_DIR))
a = ap.parse_args()

cfg = ladder.load_config()
state, plan = ladder.plan(cfg, ladder.read_state(cfg, a.data_dir), ladder.read_history(a.data_dir), date.fromisoformat(a.date))
ladder.write_state(state, a.data_dir)

cards = json.loads(Path(a.cards).read_text())
for c in cards:
    if isinstance(c["options"], str):
        c["options"] = json.loads(c["options"])
if a.comic:
    comic = json.loads(Path(a.comic).read_text())
else:
    comic = {"src": "data:image/png;base64," + base64.b64encode((HERE / "comic.png").read_bytes()).decode(),
             "page": "https://explosm.net/comics/waaah-waaah"}
d = date.fromisoformat(a.date)
data = {
    "date": a.date,
    "dateline": d.strftime("%A, %B ") + str(d.day),
    "dueTotal": len(cards),
    "cards": [{k: c[k] for k in ("card_id", "prompt", "answer", "elaboration", "options", "correct_index")} for c in cards],
    "events": json.loads(Path(a.events).read_text()) if a.events else [],
    "plan": plan,
    "threadUrl": a.thread_url,
    "comic": comic,
}
html = (HERE / "template.html").read_text().replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
Path(a.out).write_text(html)
print(a.out)
