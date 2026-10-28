#!/usr/bin/env python3
"""Export a sanitized copy of Matt's agent setup to slub-hq so Tyler's agents can adopt it.

Copies: compiled rules (CLAUDE.md), the Code-tab coordinator doc, and Matt's own `_` skills
into ~/projects/slub-hq/setup/matt/, strips private bits, then commits and pushes slub-hq.
Run by build_rules.py; safe to run by hand. --no-push to skip git.
"""
import hashlib, re, shutil, subprocess, sys
from datetime import date
from pathlib import Path

HOME = Path.home()
AIOS = HOME / "projects/ai-os"
HQ = HOME / "projects/slub-hq"
OUT = HQ / "setup/matt"

# Lines mentioning these are dropped entirely (private files/people/school).
DROP = re.compile(r"identity\.md|private/|SCHOOL\.md|school|PHIL|student|Kristy|girlfriend|health|\.env\b", re.I)
SUBS = [
    (re.compile(r"/Users/matt(hewmurphy)?"), "~"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "<email>"),
    (re.compile(r"(?<![\w-])(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?![\w-])"), "<phone>"),
    (re.compile(r"\b(cmsg|chan|local|session)_[A-Za-z0-9-]{6,}"), r"\1_<id>"),
]
SECRET = re.compile(r"(sk-|ghp_|AKIA|AIza)[A-Za-z0-9_-]{12,}|BEGIN [A-Z ]*PRIVATE KEY")


def clean(text: str) -> str:
    out = []
    for line in text.splitlines():
        if DROP.search(line):
            continue
        for rx, rep in SUBS:
            line = rx.sub(rep, line)
        out.append(line)
    text = "\n".join(out) + "\n"
    if SECRET.search(text):
        raise SystemExit("export_setup: secret-looking string found; aborting")
    return text


def put(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(clean(src.read_text(errors="ignore")))


def sections(text: str) -> dict:
    """Split rules into {heading: set(lines)} so changes can be reported per section."""
    out, head = {}, "(top)"
    for line in text.splitlines():
        if line.startswith("#"):
            head = line.lstrip("# ").strip()
        elif line.strip():
            out.setdefault(head, []).append(line)
    return out


def log_changes(old: str, new: str, changes: Path):
    """Append new/changed rule lines to CHANGES.md; Tyler's agent asks him about each entry."""
    if not old:
        return
    before, after = sections(old), sections(new)
    entries = []
    for head, lines in after.items():
        seen = set(before.get(head, []))
        added = [l for l in lines if l not in seen]
        if added:
            rid = hashlib.sha1((head + "\n".join(added)).encode()).hexdigest()[:8]
            entries.append(f"## {rid} · {date.today()} · {head}\n\n" + "\n".join(added) + "\n")
    if entries:
        prev = changes.read_text() if changes.exists() else CHANGES_HEAD
        changes.write_text(prev.rstrip() + "\n\n" + "\n".join(entries))


CHANGES_HEAD = ("# New rules from Matt\n\n"
                "One entry per new or changed rule section, newest last. Tyler's agent explains each in plain words "
                "and asks Yes / No / Ask me later (see ../INSTALL.md). Entry id = the 8 characters after `##`.\n")


# Optional desktop mods Tyler's agent can offer (each with the Mac helpers it needs).
MODS = ["read-aloud", "action-bar"]
MOD_HELPERS = [  # (source, path under setup/matt/mods/)
    (HOME / ".hammerspoon/modules/claude_read_aloud.lua", "hammerspoon/modules/claude_read_aloud.lua"),
    (HOME / ".hammerspoon/modules/claude_control.lua", "hammerspoon/modules/claude_control.lua"),
    (HOME / ".hammerspoon/modules/tweaks.lua", "hammerspoon/modules/tweaks.lua"),
    (HOME / ".hammerspoon/bin/claude-control", "hammerspoon/bin/claude-control"),
    (AIOS / "scripts/dictate.sh", "scripts/dictate.sh"),
    (AIOS / "scripts/hooks/live_call.py", "scripts/hooks/live_call.py"),
]


def export_mods():
    root = OUT / "mods"
    for name in MODS:
        for f in (AIOS / "mods" / name).rglob("*"):
            if f.is_file() and "node_modules" not in f.parts:
                put(f, root / name / f.relative_to(AIOS / "mods" / name))
    names = set(MODS)
    mk = __import__("json").loads((AIOS / "mods/.claude-plugin/marketplace.json").read_text())
    mk["name"], mk["owner"] = "slub-mods", {"name": "Matt (via slub-hq)"}
    mk["plugins"] = [p for p in mk["plugins"] if p["name"] in names]
    (root / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (root / ".claude-plugin/marketplace.json").write_text(__import__("json").dumps(mk, indent=2) + "\n")
    for src, rel in MOD_HELPERS:
        if src.exists():
            put(src, root / rel)


def main():
    if not HQ.exists():
        print("export_setup: slub-hq not found, skipping"); return
    old_rules = (OUT / "rules.md").read_text() if (OUT / "rules.md").exists() else ""
    old_changes = (OUT / "CHANGES.md").read_text() if (OUT / "CHANGES.md").exists() else None
    if OUT.exists():
        shutil.rmtree(OUT)  # generated folder, fully rebuilt each run
    put(AIOS / "CLAUDE.md", OUT / "rules.md")
    coord = AIOS / "docs/coordinator/code-coordinator.md"
    if coord.exists():
        put(coord, OUT / "coordinator.md")
    pc = AIOS / "docs/coordinator/project-coordinator.md"
    if pc.exists():
        put(pc, OUT / "project-coordinator.md")
    if old_changes is not None:
        (OUT / "CHANGES.md").write_text(old_changes)
    log_changes(old_rules, (OUT / "rules.md").read_text(), OUT / "CHANGES.md")
    export_mods()
    for skill in sorted((AIOS / "skills").glob("_*/SKILL.md")):
        put(skill, OUT / "skills" / skill.parent.name / "SKILL.md")
    (OUT / "README.md").write_text(
        "# Matt's agent setup (auto-exported)\n\n"
        "Generated by ai-os `scripts/export_setup.py` whenever Matt's rules are rebuilt. Don't edit here; edits get overwritten.\n\n"
        "- `rules.md`: Matt's global agent rules (private lines removed, paths shortened to `~`).\n"
        "- `coordinator.md`: how his Code-tab coordinator session routes work to threads.\n"
        "- `project-coordinator.md`: per-project coordinators under the central one.\n"
        "- `CHANGES.md`: new rules, one entry each; Tyler's agent offers them to him (Yes / No / Ask me later).\n"
        "- `mods/`: optional Claude desktop mods (read-aloud, action-bar) + the Mac helpers they need; see ../INSTALL.md step 8.\n"
        "- `skills/`: his custom skills (`_` prefix).\n\n"
        "Tyler: setup is in `../INSTALL.md`. Shared Slub rules (`../core.md`) sync automatically; "
        "everything here is optional. Skip Mac-specific bits (Hammerspoon, do.test, claude-control) unless you set those up too.\n")
    if "--no-push" in sys.argv:
        print(f"export_setup: wrote {OUT}"); return
    g = lambda *a: subprocess.run(["git", "-C", str(HQ), *a], capture_output=True, text=True)
    g("add", "setup/matt")
    if g("diff", "--cached", "--quiet").returncode == 0:
        print("export_setup: no changes"); return
    g("commit", "-m", "Update Matt's exported agent setup")
    r = g("pull", "--rebase", "-q"); r = g("push", "-q")
    print("export_setup: pushed" if r.returncode == 0 else f"export_setup: push failed: {r.stderr.strip()}")


if __name__ == "__main__":
    main()
