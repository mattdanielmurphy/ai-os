#!/usr/bin/env python3
"""Print a clickable markdown link for a file or folder on Matt's Mac.

Chat drops vscode:// and file:// links, so links go through Hammerspoon's action-link
server (~/.hammerspoon/modules/path_links.lua): folder -> Finder, text file -> VS Code,
anything else -> revealed in Finder.

  file_link.py ~/projects/ai-os/AG_CONTEXT.md          -> [AG_CONTEXT.md](http://do.test/open/...)
  file_link.py ~/projects --label "projects folder"
  file_link.py --url ~/projects                        -> bare URL only
"""
import argparse
import os
import sys
from urllib.parse import quote

BASE = "http://do.test/open"


def url_for(path: str) -> str:
    path = os.path.abspath(os.path.expanduser(path))
    return BASE + quote(path, safe="/-._~")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--label", help="link text (default: the file or folder name)")
    ap.add_argument("--url", action="store_true", help="print only the URL")
    args = ap.parse_args()
    for p in args.paths:
        full = os.path.abspath(os.path.expanduser(p))
        if not os.path.exists(full):
            print(f"missing: {full}", file=sys.stderr)
        u = url_for(full)
        if args.url:
            print(u)
        else:
            label = args.label or os.path.basename(full.rstrip("/")) or full
            if os.path.isdir(full):
                label += "/"
            print(f"[{label}]({u})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
