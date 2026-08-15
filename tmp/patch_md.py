#!/usr/bin/env python3
"""
Patch all .md files in gemini_history_export/stitched_markdown and
gemini-archive/threads to ensure every '<!-- gemini-message' block has a
proper '<!-- /gemini-message -->' closing tag.

Missing closing tags are inserted right before the next '---' separator,
or at the end of the file if no separator follows the open block.
"""

import os
import re
import sys

# Directories to scan
DIRS = [
    "/Users/matt/Downloads/gemini_history_export/stitched_markdown",
    "/Users/matt/Documents/gemini-archive/threads",
]

# Pattern: opening gemini-message comment (possibly with attributes)
OPEN_PATTERN = re.compile(r"<!--\s*gemini-message")
# Pattern: closing gemini-message comment
CLOSE_PATTERN = re.compile(r"<!--\s*/gemini-message\s*-->")
# Separator line (optional leading/trailing whitespace)
SEP_PATTERN = re.compile(r"^---+$")


def patch_file(filepath: str) -> bool:
    """Patch a single file. Returns True if changes were made."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()

    lines = raw.splitlines(keepends=True)
    # Work on text without line-endings for easier regex matching
    text = raw

    # Find all opening tags and closing tags by position
    open_positions = [m.end() for m in OPEN_PATTERN.finditer(text)]
    close_positions = [m.start() for m in CLOSE_PATTERN.finditer(text)]

    # Walk openings and count how many are unmatched
    # A closing tag matches the nearest preceding open tag
    open_stack: list[int] = []  # stores end position of each open tag
    for op in open_positions:
        open_stack.append(op)
        # Pop for any close that falls after this open
        # (simple greedy: each close closes the most recent open)
        while close_positions and close_positions[0] < op:
            close_positions.pop(0)
        if close_positions and close_positions[0] > op:
            close_positions.pop(0)
            open_stack.pop()

    # Anything left in open_stack is missing a close tag
    unmatched = len(open_stack)
    if unmatched == 0:
        return False

    print(f"  → {unmatched} unmatched block(s)")

    # Walk through lines and insert close tags
    insertions: list[tuple[int, str]] = []  # (line_index, text_to_insert)
    depth = 0
    i = 0
    while i < len(lines):
        line = lines[i]

        if OPEN_PATTERN.search(line):
            depth += 1
            print(f"    [depth={depth}] open: {line.strip()[:80]}")

        # Check for close on this line
        if CLOSE_PATTERN.search(line):
            if depth > 0:
                depth -= 1
                print(f"    [depth={depth}] close: {line.strip()[:80]}")

        # If we have open blocks and hit a separator (or end of file),
        # insert missing close tags before the separator.
        if depth > 0 and SEP_PATTERN.match(line.strip()):
            for _ in range(depth):
                insertions.append((i, "<!-- /gemini-message -->\n"))
                print(f"    → inserted close before line {i+1}: {line.strip()}")
            depth = 0

        i += 1

    # Any remaining depth at EOF
    if depth > 0:
        for _ in range(depth):
            insertions.append((len(lines), "<!-- /gemini-message -->\n"))
            print(f"    → inserted close at end of file (depth={depth})")
        depth = 0

    # Apply insertions (reverse order to preserve indices)
    insertions.sort(key=lambda x: x[0], reverse=True)
    for idx, txt in insertions:
        lines.insert(idx, txt)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)

    return True


def main() -> int:
    total_files = 0
    total_patched = 0

    for directory in DIRS:
        if not os.path.isdir(directory):
            print(f"[SKIP] Directory not found: {directory}")
            continue

        print(f"\n{'='*60}")
        print(f"Scanning: {directory}")
        print(f"{'='*60}")

        for root, _dirs, files in os.walk(directory):
            for fname in sorted(files):
                if not fname.endswith(".md"):
                    continue
                fpath = os.path.join(root, fname)
                total_files += 1
                rel = os.path.relpath(fpath, directory)
                print(f"\n[{total_files}] {rel}")
                try:
                    changed = patch_file(fpath)
                    if changed:
                        total_patched += 1
                        print(f"  ✔ Patched")
                    else:
                        print(f"  ✓ OK (all blocks closed)")
                except Exception as e:
                    print(f"  ✗ ERROR: {e}", file=sys.stderr)

    print(f"\n{'='*60}")
    print(f"Done. {total_patched} of {total_files} files patched.")
    print(f"{'='*60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())