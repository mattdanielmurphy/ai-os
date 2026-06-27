#!/usr/bin/env python3
import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="Safely perform direct file modifications.")
    parser.add_argument("--file", required=True, help="Absolute path to the target file")
    parser.add_argument("--mode", required=True, choices=["replace", "append", "insert_after_string"], help="Modification mode")
    parser.add_argument("--target", help="Exact string to find (required for replace and insert_after_string)")
    parser.add_argument("--content", required=True, help="The new content to insert/replace")

    args = parser.parse_args()

    # Validate target requirements
    if args.mode in ["replace", "insert_after_string"] and args.target is None:
        print("Error: --target is required for mode 'replace' and 'insert_after_string'.", file=sys.stderr)
        sys.exit(1)

    filepath = os.path.abspath(args.file)
    if not os.path.isabs(args.file):
        print(f"Error: File path '{args.file}' is not absolute.", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' does not exist.", file=sys.stderr)
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        file_content = f.read()

    if args.mode == "replace":
        count = file_content.count(args.target)
        if count == 0:
            print(f"Error: Target string not found in '{filepath}'.", file=sys.stderr)
            sys.exit(1)
        elif count > 1:
            print(f"Error: Target string found {count} times (expected exactly 1) in '{filepath}'.", file=sys.stderr)
            sys.exit(1)
        
        new_content = file_content.replace(args.target, args.content)
        
    elif args.mode == "append":
        new_content = file_content + args.content
        
    elif args.mode == "insert_after_string":
        lines = file_content.splitlines(keepends=True)
        matching_indices = [i for i, line in enumerate(lines) if args.target in line]
        if len(matching_indices) == 0:
            print(f"Error: Target string not found in any line of '{filepath}'.", file=sys.stderr)
            sys.exit(1)
        elif len(matching_indices) > 1:
            print(f"Error: Target string found in multiple lines: {matching_indices} of '{filepath}'.", file=sys.stderr)
            sys.exit(1)
            
        idx = matching_indices[0]
        target_line = lines[idx]
        if not target_line.endswith("\n"):
            lines[idx] = target_line + "\n"
        
        insert_content = args.content
        if not insert_content.endswith("\n"):
            insert_content += "\n"
            
        lines.insert(idx + 1, insert_content)
        new_content = "".join(lines)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Success: File '{filepath}' modified successfully in '{args.mode}' mode.")

if __name__ == "__main__":
    main()
