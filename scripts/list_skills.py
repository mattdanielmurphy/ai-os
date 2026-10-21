#!/usr/bin/env python3
"""List every skill Claude can load, newest first, split into Matt's own and stock.

Backs the `_list-skills` skill. Prints markdown so it reads well in chat.

Sources:
- ~/.claude/skills/<name>/SKILL.md (and ./.claude/skills in the current project)
  - stock when listed in Hermes' .bundled_manifest or .webui-managed-skills.json
  - everything else is Matt's
- Claude app account skills (manifest.json, creatorType "anthropic" = stock)
- Claude app plugins (design, productivity, pdf-viewer, ...) and Claude Code plugins
"""
import argparse
import glob
import json
import re
from datetime import date, datetime
from pathlib import Path

HOME = Path.home()
USER_SKILLS = HOME / ".claude" / "skills"
AIOS_SKILLS = HOME / "projects" / "ai-os" / "skills"
APP_SESSIONS = HOME / "Library" / "Application Support" / "Claude" / "local-agent-mode-sessions"
CODE_PLUGINS = HOME / ".claude" / "plugins"


def frontmatter(path):
    """Return (name, description) from a SKILL.md's YAML frontmatter."""
    try:
        text = path.read_text(errors="replace")
    except OSError:
        return None, ""
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m:
        return None, ""
    fields, key = {}, None
    for line in m.group(1).splitlines():
        k, sep, v = line.partition(":")
        if sep and not line.startswith((" ", "\t")):
            key = k.strip()
            v = v.strip()
            # Block scalars (`description: >`) continue on indented lines.
            fields[key] = "" if v in (">", "|", ">-", "|-") else v.strip("\"'")
        elif key and line.startswith((" ", "\t")):
            fields[key] = (fields[key] + " " + line.strip()).strip()
    return fields.get("name"), fields.get("description", "")


def created(*paths):
    """Earliest creation date among the paths that exist."""
    days = []
    for p in paths:
        try:
            st = p.stat()
        except OSError:
            continue
        days.append(date.fromtimestamp(getattr(st, "st_birthtime", st.st_mtime)))
    return min(days) if days else None


def hermes_stock():
    names = set()
    manifest = USER_SKILLS / ".bundled_manifest"
    if manifest.exists():
        names |= {line.split(":")[0] for line in manifest.read_text().split() if ":" in line}
    webui = USER_SKILLS / ".webui-managed-skills.json"
    if webui.exists():
        try:
            names |= set(json.loads(webui.read_text()))
        except ValueError:
            pass
    return names


def local_skills(root, stock_names, label):
    mine, stock = [], []
    if not root.is_dir():
        return mine, stock
    for d in sorted(root.iterdir()):
        md = d / "SKILL.md"
        if not md.is_file():
            continue
        name, desc = frontmatter(md)
        entry = {
            "name": d.name,
            "desc": desc,
            "date": created(md, AIOS_SKILLS / d.name / "SKILL.md"),
            "where": label,
        }
        if d.name in stock_names or (name and name in stock_names):
            entry["where"] = "Hermes bundle"
            stock.append(entry)
        else:
            mine.append(entry)
    return mine, stock


def account_skills():
    mine, stock = [], []
    for mf in glob.glob(str(APP_SESSIONS / "skills-plugin" / "*" / "*" / "manifest.json")):
        try:
            data = json.loads(Path(mf).read_text())
        except (OSError, ValueError):
            continue
        for s in data.get("skills", []):
            if s.get("enabled") is False:
                continue
            stamp = s.get("createdAt") or s.get("updatedAt")
            day = datetime.fromisoformat(stamp.replace("Z", "+00:00")).date() if stamp else None
            entry = {"name": s.get("name", "?"), "desc": s.get("description", ""), "date": day}
            if s.get("creatorType") == "anthropic":
                entry["where"] = "Claude app (Anthropic)"
                stock.append(entry)
            else:
                entry["where"] = "claude.ai account"
                mine.append(entry)
    return mine, stock


def plugin_skills():
    """Skills shipped by Claude app plugins and installed Claude Code plugins."""
    out = []
    seen = set()
    for pj in glob.glob(str(APP_SESSIONS / "*" / "*" / "rpm" / "*" / ".claude-plugin" / "plugin.json")):
        root = Path(pj).parent.parent
        try:
            plugin = json.loads(Path(pj).read_text()).get("name", root.name)
        except (OSError, ValueError):
            plugin = root.name
        for md in sorted(root.glob("skills/*/SKILL.md")):
            key = f"{plugin}:{md.parent.name}"
            if key in seen:
                continue
            seen.add(key)
            out.append({"name": key, "desc": frontmatter(md)[1], "date": created(md),
                        "where": "Claude app plugins"})
    try:
        installed = json.loads((CODE_PLUGINS / "installed_plugins.json").read_text()).get("plugins", {})
    except (OSError, ValueError):
        installed = {}
    for key, installs in installed.items():
        plugin, _, market = key.partition("@")
        for inst in installs if isinstance(installs, list) else [installs]:
            path = Path(inst.get("installPath", "")) if isinstance(inst, dict) else None
            if not path:
                continue
            for md in sorted(path.glob("skills/*/SKILL.md")):
                out.append({"name": f"{plugin}:{md.parent.name}", "desc": frontmatter(md)[1],
                            "date": created(md),
                            "where": "my mods" if market == "ai-os-mods" else "Claude Code plugins"})
    return out


def newest_first(items):
    return sorted(items, key=lambda e: (e["date"] or date.min, e["name"]), reverse=True)


def short(text, n):
    text = " ".join(text.split()).replace("|", "/")
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--mine", action="store_true", help="only Matt's own skills")
    ap.add_argument("--stock", action="store_true", help="only stock skills")
    ap.add_argument("--find", help="only skills whose name or description contains this text")
    ap.add_argument("--width", type=int, default=90, help="description length in the table")
    args = ap.parse_args()

    stock_names = hermes_stock()
    mine, stock = local_skills(USER_SKILLS, stock_names, "~/.claude/skills")
    pm, ps = local_skills(Path.cwd() / ".claude" / "skills", stock_names, "this project")
    am, ast = account_skills()
    mine += pm + am
    stock += ps + ast
    for p in plugin_skills():
        (mine if p["where"] == "my mods" else stock).append(p)

    if args.find:
        q = args.find.lower()
        mine = [e for e in mine if q in e["name"].lower() or q in e["desc"].lower()]
        stock = [e for e in stock if q in e["name"].lower() or q in e["desc"].lower()]

    if not args.stock:
        print(f"## My skills ({len(mine)}), newest first\n")
        print("| Added | Skill | What it does |")
        print("|---|---|---|")
        for e in newest_first(mine):
            day = e["date"].isoformat() if e["date"] else "?"
            where = "" if e["where"] == "~/.claude/skills" else f" ({e['where']})"
            print(f"| {day} | `/{e['name']}`{where} | {short(e['desc'], args.width)} |")
        print()
        if not args.find:
            print("Not a skill, but easy to forget: in a Claude project thread, start a message "
                  "with `/coord` to send it to the project coordinator instead of the thread.\n")

    if not args.mine:
        groups = {}
        for e in newest_first(stock):
            groups.setdefault(e["where"], []).append(e)
        print(f"## Stock skills ({len(stock)}), newest first\n")
        for where, items in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            names = ", ".join(e["name"] for e in items)
            print(f"- **{where} ({len(items)}):** {names}")
        if not args.find:
            print("- **Claude Code built-ins:** type `/` to see them (simplify, loop, code-review, …)")


if __name__ == "__main__":
    main()
