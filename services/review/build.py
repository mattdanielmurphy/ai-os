#!/usr/bin/env python3
"""Build a review page: a long agent reply, one card per section, tap-a-sentence comments.

Usage: build.py REPLY.md --id ID [--title T] [--page ARTIFACT_ID] [--thread cmsg_…] [--out F]

Sections are the reply's `## ` headings (or `### ` if it has none); text before the first heading
is an "Intro" card. --page is the artifact's own id (claude.ai/artifact/<id>), known after the
first publish: build, publish, then rebuild with --page and publish again so Done can name it.
The Done link points at the Mac connector's /act route (services/mac-connector); its base URL is
read from tmp/mac-connector-act-url, which the connector writes on start.
Matt's ticks and notes land in the page's db at reviews/<ID> (read them with ArtifactData).
"""
import argparse, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
AIOS = HERE.parent.parent
ACT_FILE = Path.home() / "projects" / "ai-os" / "tmp" / "mac-connector-act-url"


def split_sections(md: str) -> list[dict]:
    level = "## " if re.search(r"^## ", md, re.M) else "### "
    parts = re.split(rf"^{level}(.+)$", md, flags=re.M)
    out = []
    if parts[0].strip():
        out.append({"title": "Intro", "md": parts[0].strip()})
    for title, body in zip(parts[1::2], parts[2::2]):
        out.append({"title": title.strip(), "md": body.strip()})
    for i, s in enumerate(out):
        s["id"] = f"s{i + 1}"
    return out


def build(md: str, *, id: str, title: str, page: str = "", thread: str = "", act: str = "") -> str:
    data = {"id": id, "title": title, "page": page, "thread": thread, "act": act, "sections": split_sections(md)}
    html = (HERE / "template.html").read_text()
    html = html.replace("/*__KIT_CSS__*/", (HERE.parent / "pages" / "kit.css").read_text())
    html = html.replace("__TITLE__", title.replace("<", "&lt;"))
    return html.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("reply")
    ap.add_argument("--id", required=True)
    ap.add_argument("--title", default="Review")
    ap.add_argument("--page", default="")
    ap.add_argument("--thread", default="")
    ap.add_argument("--out")
    a = ap.parse_args()
    act = ACT_FILE.read_text().strip() if ACT_FILE.exists() else ""
    out = Path(a.out or AIOS / "tmp" / "review" / f"{a.id}.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(Path(a.reply).read_text(), id=a.id, title=a.title, page=a.page, thread=a.thread, act=act))
    print(out)
