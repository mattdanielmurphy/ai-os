#!/usr/bin/env python3
"""Build the habit gate's study page with the check-in's flashcard layout (template.html, practice mode).

Usage: practice.py CARDS.json [--date YYYY-MM-DD] [--title T] [--deck D] [--out F]

CARDS.json: a list of {"prompt", "key"?, "options": [...], "correct_index", "answer", "elaboration"}.
"key" is an optional symbol key shown under the prompt, one item per line (a list, or "·"-separated). card_id is filled in.
Publish the output with the `db` capability so taps are saved under practice/<date>.
"""
import argparse, json, re
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent


def key_lines(key):
    """Symbol key, one item per line (Matt: newlines, not "·" separators)."""
    if isinstance(key, list):
        return "\n".join(key)
    return "\n".join(k.strip() for k in re.split(r"\s*[·;]\s*|\n", key) if k.strip())


def build(cards, day, title, deck):
    cards = [{"card_id": c.get("card_id") or f"practice_{day}_q{i + 1}",
              "prompt": c["prompt"], "key": key_lines(c.get("key", "")), "options": c["options"],
              "correct_index": c["correct_index"], "answer": c["answer"], "elaboration": c.get("elaboration", "")}
             for i, c in enumerate(cards)]
    for c in cards:
        assert 0 <= c["correct_index"] < len(c["options"]), c["card_id"]
    d = date.fromisoformat(day)
    data = {"mode": "practice", "date": day, "dateline": d.strftime("%A, %B ") + str(d.day),
            "title": title, "deck": deck, "dueTotal": len(cards), "cards": cards,
            "plan": {"doses": {"cards": len(cards)}, "steps": [], "changes": []}}
    html = (HERE / "template.html").read_text()
    html = html.replace("<title>Morning Check-In</title>", f"<title>{title}</title>", 1)
    return html.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cards")
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--title", default="Logic practice")
    ap.add_argument("--deck", default="PHIL 120 · Symbolic Logic")
    ap.add_argument("--out")
    a = ap.parse_args()
    out = Path(a.out or HERE / "data" / "build" / f"practice-{a.date}.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(json.loads(Path(a.cards).read_text()), a.date, a.title, a.deck))
    print(out)
