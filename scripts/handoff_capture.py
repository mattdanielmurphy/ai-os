#!/usr/bin/env python3
"""Copy Matt's /_handoff message into a handoff file, word for word.

When Matt runs /_handoff he may add his own text, quotes ("<!-- reply N -->" + "> ..."),
quote-with-comments, element selections and images. Retyping that loses detail, so this
script reads the turn straight from the Claude Code transcript and:

- appends a "Matt's message with this handoff (verbatim)" section to the handoff file,
  with every text block in a fence the content can't break out of;
- decodes each pasted image to <handoff stem>/image-N.<ext> and links it;
- copies any ~/.claude/uploads/... files the message names into the same folder.

Usage:
  python3 scripts/handoff_capture.py --handoff docs/handoffs/<file>.md [--session <id>]
Session defaults to $CLAUDE_CODE_SESSION_ID. Run it once, after the handoff file is written.
"""
import argparse
import base64
import glob
import json
import os
import re
import shutil
import sys

SECTION = "## Matt's message with this handoff (verbatim)"
SKILL_BODY_PREFIX = "Base directory for this skill:"
UPLOAD_RE = re.compile(r"(?:~|/Users/[^/\s]+)/\.claude/uploads/[^\s\"'`)>\]]+")
EXT = {"image/png": "png", "image/jpeg": "jpg", "image/gif": "gif", "image/webp": "webp"}


def find_transcript(session_id):
    hits = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{session_id}.jsonl"))
    if not hits:
        sys.exit(f"No transcript found for session {session_id}")
    return max(hits, key=os.path.getmtime)


def load(path):
    out = []
    with open(path) as f:
        for line in f:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def blocks(rec):
    c = rec.get("message", {}).get("content")
    if isinstance(c, str):
        return [{"type": "text", "text": c}]
    return c if isinstance(c, list) else []


def is_human_prompt(rec):
    """A user record Matt typed (not a tool result, not the injected skill body)."""
    if rec.get("type") != "user" or rec.get("isMeta"):
        return False
    bs = blocks(rec)
    if not bs or any(b.get("type") == "tool_result" for b in bs):
        return False
    return True


def handoff_turn(records):
    """All user records of the turn that triggered /_handoff (latest one)."""
    idx = None
    for i, r in enumerate(records):
        if is_human_prompt(r) and any(
            "<command-name>/_handoff</command-name>" in (b.get("text") or "") for b in blocks(r)
        ):
            idx = i
    if idx is None:  # skill invoked by the model from plain words ("hand this off")
        for i, r in enumerate(records):
            if is_human_prompt(r):
                idx = i
    if idx is None:
        return []
    pid = records[idx].get("promptId")
    if pid:
        turn = [r for r in records if r.get("promptId") == pid and r.get("type") == "user"]
    else:
        turn = [records[idx]]
    keep = []
    for r in turn:
        bs = [b for b in blocks(r) if not (b.get("text") or "").startswith(SKILL_BODY_PREFIX)]
        if bs and not any(b.get("type") == "tool_result" for b in bs):
            keep.append(bs)
    return keep


def clean_command_text(t):
    """Turn the slash-command wrapper into what Matt typed: '/_handoff <args>'."""
    if "<command-name>" not in t:
        return t
    args = re.search(r"<command-args>(.*?)</command-args>", t, re.S)
    args = args.group(1) if args else ""
    rest = re.sub(r"<command-(?:name|message|args)>.*?</command-(?:name|message|args)>", "", t, flags=re.S)
    return ("/_handoff " + args).rstrip() + ("\n" + rest.strip() if rest.strip() else "")


def fence(text):
    longest = max((len(m) for m in re.findall(r"`{3,}", text)), default=2)
    f = "`" * (longest + 1)
    return f"{f}text\n{text}\n{f}"


def render(turn_blocks, asset_dir, rel_dir):
    parts, n_img, copied = [], 0, set()
    for bs in turn_blocks:
        for b in bs:
            t = b.get("type")
            if t == "text":
                text = clean_command_text(b["text"])
                if not text.strip():
                    continue
                parts.append(fence(text))
                for p in UPLOAD_RE.findall(text):
                    src = os.path.expanduser(p)
                    if os.path.isfile(src) and src not in copied:
                        os.makedirs(asset_dir, exist_ok=True)
                        shutil.copy2(src, os.path.join(asset_dir, os.path.basename(src)))
                        copied.add(src)
                        parts.append(f"- Attached file `{p}` copied to `{rel_dir}/{os.path.basename(src)}`")
            elif t == "image":
                src = b.get("source", {})
                if src.get("type") != "base64":
                    parts.append(f"- (image of source type {src.get('type')!r} not saved)")
                    continue
                n_img += 1
                os.makedirs(asset_dir, exist_ok=True)
                name = f"image-{n_img}.{EXT.get(src.get('media_type'), 'png')}"
                with open(os.path.join(asset_dir, name), "wb") as f:
                    f.write(base64.b64decode(src["data"]))
                parts.append(f"![image {n_img}]({rel_dir}/{name})  \n`{rel_dir}/{name}` (open it with Read)")
            else:
                parts.append(f"- (unhandled block type {t!r})")
    return parts, n_img, len(copied)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--handoff", required=True)
    ap.add_argument("--session", default=os.environ.get("CLAUDE_CODE_SESSION_ID"))
    ap.add_argument("--transcript", help="override transcript path (tests)")
    a = ap.parse_args(argv)
    if not a.session and not a.transcript:
        sys.exit("No session id: pass --session or set CLAUDE_CODE_SESSION_ID")

    handoff = os.path.abspath(a.handoff)
    body = open(handoff).read()
    if SECTION in body:
        sys.exit(f"{handoff} already has the verbatim section; not adding it twice")

    turn = handoff_turn(load(a.transcript or find_transcript(a.session)))
    stem = os.path.splitext(os.path.basename(handoff))[0]
    asset_dir = os.path.join(os.path.dirname(handoff), stem)
    parts, n_img, n_files = render(turn, asset_dir, stem)

    intro = (
        "Exactly what Matt sent with `/_handoff`, copied from the transcript by "
        "`scripts/handoff_capture.py`. Treat it as his instructions for the next thread. "
        "Quotes (`> ...` after `<!-- reply N -->`) are from the previous thread's replies; "
        "the text under each quote is his comment on it. Open every image listed."
    )
    section = f"\n\n{SECTION}\n\n{intro}\n\n" + ("\n\n".join(parts) if parts else "(nothing found)") + "\n"
    with open(handoff, "w") as f:
        f.write(body.rstrip("\n") + section)
    print(f"Appended verbatim section: {len(parts)} parts, {n_img} images, {n_files} files -> {asset_dir if (n_img or n_files) else 'no assets'}")


if __name__ == "__main__":
    main()
