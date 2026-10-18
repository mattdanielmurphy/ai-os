#!/usr/bin/env python3
"""Build the morning check-in page from template.html.

Usage: build.py [--date YYYY-MM-DD] [--thread-url URL] [--out morning-checkin.html]
Today's doses come from ladder.py (habit ladder); cards.json and comic.png are the current inputs.
"""
import argparse, base64, json
from datetime import date
from pathlib import Path

import ladder

HERE = Path(__file__).resolve().parent

ap = argparse.ArgumentParser()
ap.add_argument("--date", default=date.today().isoformat())
ap.add_argument("--thread-url", default="", help="claude:// link to today's Sonnet reflection thread")
ap.add_argument("--out", default=str(HERE / "morning-checkin.html"))
ap.add_argument("--data-dir", default=str(ladder.DATA_DIR))
a = ap.parse_args()

cfg = ladder.load_config()
state, plan = ladder.plan(cfg, ladder.read_state(cfg, a.data_dir), ladder.read_history(a.data_dir), date.fromisoformat(a.date))
ladder.write_state(state, a.data_dir)

cards = json.loads((HERE / "cards.json").read_text())
for c in cards:
    c["options"] = json.loads(c["options"])
d = date.fromisoformat(a.date)
data = {
    "date": a.date,
    "dateline": d.strftime("%A, %B ") + str(d.day),
    "dueTotal": len(cards),
    "cards": [{k: c[k] for k in ("card_id", "prompt", "answer", "elaboration", "options", "correct_index")} for c in cards],
    "events": [],
    "plan": plan,
    "threadUrl": a.thread_url,
    "comic": {"src": "data:image/png;base64," + base64.b64encode((HERE / "comic.png").read_bytes()).decode(),
              "page": "https://explosm.net/comics/waaah-waaah"},
}
html = (HERE / "template.html").read_text().replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
Path(a.out).write_text(html)
print(a.out)
