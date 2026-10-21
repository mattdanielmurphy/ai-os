#!/usr/bin/env python3
"""Print voice-call transcripts compactly for review, and track which ones were reviewed.

  review_voice_calls.py                 # every transcript not yet marked reviewed
  review_voice_calls.py <path> ...      # just these (vault-relative or absolute)
  review_voice_calls.py --done <path>…  # mark reviewed after filing facts / reminders
"""
import json, re, sys
from pathlib import Path

VAULT = Path.home() / "Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal"
TRANSCRIPTS = VAULT / "Voice calls/Transcripts"
STATE = Path(__file__).resolve().parent.parent / "tmp/voice-call-review/reviewed.json"


def resolve(p):
    p = Path(p)
    return p if p.is_absolute() else VAULT / p


def compact(text):
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)  # frontmatter
    text = re.sub(r"_\(used [^)]*\)_\n*", "", text)  # tool-use markers
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def main(args):
    reviewed = json.loads(STATE.read_text()) if STATE.exists() else {}
    if args[:1] == ["--done"]:
        for a in args[1:]:
            reviewed[resolve(a).name] = True
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps(reviewed, indent=1))
        print(f"marked {len(args) - 1} reviewed")
        return 0
    files = [resolve(a) for a in args] or sorted(f for f in TRANSCRIPTS.glob("*.md") if f.name not in reviewed)
    if not files:
        print("nothing to review")
    for f in files:
        print(f"===== {f.relative_to(VAULT) if f.is_relative_to(VAULT) else f}\n{compact(f.read_text())}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
