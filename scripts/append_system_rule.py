#!/usr/bin/env python3
import os
import argparse
import re
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Append a rule to GEMINI.md")
    parser.add_argument("--agent", choices=["agy", "claude", "global"], required=True, help="Target agent")
    parser.add_argument("--rule", required=True, help="Markdown string of the rule")
    args = parser.parse_args()

    # Expand user home path
    gemini_path = Path("~/.gemini/GEMINI.md").expanduser()
    if not gemini_path.parent.exists():
        gemini_path.parent.mkdir(parents=True, exist_ok=True)

    if gemini_path.exists():
        with open(gemini_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = "<SYSTEM_INSTRUCTIONS>\n</SYSTEM_INSTRUCTIONS>\n"

    # Map agent to header
    header_map = {
        "global": "### GLOBAL RULES",
        "agy": "### ANTIGRAVITY (PREMIUM) RULES",
        "claude": "### CLAUDE (ECONOMY) RULES"
    }
    target_header = header_map[args.agent]

    # Let's see if the header exists
    header_pattern = re.escape(target_header)
    if re.search(r'^' + header_pattern, content, re.MULTILINE):
        # Header exists. Find where the header block ends.
        lines = content.splitlines()
        header_idx = -1
        for idx, line in enumerate(lines):
            if line.strip() == target_header:
                header_idx = idx
                break
        
        # Scan forward to find insertion point
        insert_idx = header_idx + 1
        while insert_idx < len(lines):
            next_line = lines[insert_idx].strip()
            # If we hit another ### header or a closing tag or similar, stop
            if next_line.startswith("###") or next_line.startswith("</") or next_line.startswith("<"):
                break
            insert_idx += 1
        
        # Insert before insert_idx
        lines.insert(insert_idx, f"- {args.rule}")
        content = "\n".join(lines) + "\n"
    else:
        # Header doesn't exist. Let's insert it inside </SYSTEM_INSTRUCTIONS> if it exists, or just at the end.
        if "</SYSTEM_INSTRUCTIONS>" in content:
            parts = content.rsplit("</SYSTEM_INSTRUCTIONS>", 1)
            insertion = f"\n{target_header}\n- {args.rule}\n"
            content = parts[0].rstrip() + "\n" + insertion + "\n</SYSTEM_INSTRUCTIONS>" + parts[1]
        else:
            content = content.rstrip() + f"\n\n{target_header}\n- {args.rule}\n"

    with open(gemini_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Success: Rule successfully appended under {target_header} in {gemini_path}")

if __name__ == "__main__":
    main()
