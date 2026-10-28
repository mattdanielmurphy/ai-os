#!/usr/bin/env python3
"""Build the morning check-in page from template.html.

Usage: build.py [--date YYYY-MM-DD] [--cards F] [--out morning-checkin.html]
Today's doses come from ladder.py (habit ladder). Without --cards the fixture (cards.json) is used.
The comic and the day ahead live in the talk thread, not on the page.
"""
import argparse, json
from datetime import date
from pathlib import Path

import ladder

HERE = Path(__file__).resolve().parent

ap = argparse.ArgumentParser()
ap.add_argument("--date", default=date.today().isoformat())
ap.add_argument("--cards", default=str(HERE / "cards.json"))
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
d = date.fromisoformat(a.date)


def meditation():
    """Today's guided meditation: the ladder's level for it, and that level's track (a page asset, see meditation/)."""
    if "meditation" not in cfg["habits"]:
        return None
    levels = cfg["habits"]["meditation"]["levels"]
    minutes = ladder.dose(cfg, state, "meditation")
    level = levels.index(minutes) + 1
    assets = HERE / "meditation" / "assets.json"
    src = json.loads(assets.read_text()).get(str(level)) if assets.exists() else None
    return {"minutes": minutes, "level": level, "levels": len(levels), "src": src}


data = {
    "date": a.date,
    "dateline": d.strftime("%A, %B ") + str(d.day),
    "dueTotal": len(cards),
    "cards": [{k: c[k] for k in ("card_id", "prompt", "answer", "elaboration", "options", "correct_index")} for c in cards],
    "plan": plan,
    "meditation": meditation(),
}
html = (HERE / "template.html").read_text().replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
Path(a.out).write_text(html)
print(a.out)
