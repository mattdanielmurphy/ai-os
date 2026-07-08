#!/usr/bin/env python3
import os
import argparse
import re
from pathlib import Path

def append_rule_to_file(file_path, header, rule):
    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)

    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = "<SYSTEM_INSTRUCTIONS>\n</SYSTEM_INSTRUCTIONS>\n"

    header_pattern = re.escape(header)
    if re.search(r'^' + header_pattern, content, re.MULTILINE):
        lines = content.splitlines()
        header_idx = -1
        for idx, line in enumerate(lines):
            if line.strip() == header:
                header_idx = idx
                break
        
        insert_idx = header_idx + 1
        while insert_idx < len(lines):
            next_line = lines[insert_idx].strip()
            if next_line.startswith("###") or next_line.startswith("##") or next_line.startswith("</") or next_line.startswith("<"):
                break
            insert_idx += 1
        
        lines.insert(insert_idx, f"- {rule}")
        content = "\n".join(lines) + "\n"
    else:
        if "</SYSTEM_INSTRUCTIONS>" in content:
            parts = content.rsplit("</SYSTEM_INSTRUCTIONS>", 1)
            insertion = f"\n{header}\n- {rule}\n"
            content = parts[0].rstrip() + "\n" + insertion + "\n</SYSTEM_INSTRUCTIONS>" + parts[1]
        else:
            content = content.rstrip() + f"\n\n{header}\n- {rule}\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Success: Rule successfully appended under {header} in {file_path}")

def main():
    parser = argparse.ArgumentParser(description="Append system rules to appropriate files")
    parser.add_argument("--agent", choices=["agy", "claude", "global"], required=True, help="Target agent")
    parser.add_argument("--rule", required=True, help="Markdown string of the rule")
    args = parser.parse_args()

    gemini_path = Path("~/.gemini/GEMINI.md").expanduser()
    claude_path = Path("/Users/matt/projects/ai-os/CLAUDE.md")

    if args.agent == "global":
        append_rule_to_file(gemini_path, "### GLOBAL RULES", args.rule)
        append_rule_to_file(claude_path, "## GLOBAL RULES", args.rule)
    elif args.agent == "agy":
        append_rule_to_file(gemini_path, "### ANTIGRAVITY (PREMIUM) RULES", args.rule)
    elif args.agent == "claude":
        append_rule_to_file(claude_path, "## CLAUDE-SPECIFIC RULES", args.rule)

if __name__ == "__main__":
    main()
