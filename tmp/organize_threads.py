#!/usr/bin/env python3
"""
organize_threads.py

Loads a manifest file mapping thread IDs to (category, collection), then walks
target directories looking for .md files. For each file whose conversation_id
matches, it injects category/collection frontmatter and moves the file into a
<target>/<category>/<collection>/ subdirectory tree.
"""

import json
import os
import re
import shutil
import sys
from pathlib import Path


def load_manifest(manifest_path: str) -> dict[str, tuple[str, str]]:
    """Return {thread_id: (category_name, collection_name)} from the manifest JSON."""
    try:
        with open(manifest_path, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"[ERROR] Cannot load manifest '{manifest_path}': {exc}")
        sys.exit(1)

    mapping: dict[str, tuple[str, str]] = {}
    if isinstance(data, dict) and "categories" in data:
        for category in data["categories"]:
            cat_name = category.get("category_name", "")
            for collection in category.get("collections", []):
                col_name = collection.get("collection_name", "")
                for tid in collection.get("thread_ids", []):
                    mapping[tid] = (cat_name, col_name)
    else:
        print("[ERROR] Unrecognized manifest format.")
        sys.exit(1)

    return mapping


def read_frontmatter(content: str) -> tuple[dict[str, object], str, int]:
    """
    Parse YAML frontmatter from markdown content.

    Returns (frontmatter_dict, raw_yaml_block, end_line_index).
    Returns ({}, "", 0) when no frontmatter is found.
    """
    if not content.startswith("---"):
        return {}, "", 0

    # Find the closing ---
    end_idx = content.find("\n---", 3)
    if end_idx == -1:
        return {}, "", 0

    raw = content[3:end_idx].strip()
    fm: dict[str, object] = {}
    for line in raw.splitlines():
        # Very simple YAML key: value parsing (avoids pyyaml dependency)
        match = re.match(r'^([\w_]+)\s*:\s*(.*)', line)
        if match:
            key = match.group(1)
            value = match.group(2).strip().strip('"').strip("'")
            fm[key] = value

    end_line = content[:end_idx].count("\n") + 2  # +2 for opening/closing ---
    return fm, raw, end_line


def write_frontmatter(
    original_content: str,
    original_raw: str,
    end_line: int,
    new_fields: dict[str, str],
) -> str:
    """Return the full file content with new_fields injected into frontmatter."""
    # Rebuild frontmatter, inserting new fields alphabetically
    # Start by collecting existing lines (skip null/empty)
    existing_lines = [ln for ln in original_raw.splitlines() if ln.strip()]

    # Determine existing keys
    existing_keys: set[str] = set()
    for ln in existing_lines:
        m = re.match(r'^([\w_]+)\s*:', ln)
        if m:
            existing_keys.add(m.group(1))

    # Build new lines block
    new_lines: list[str] = []

    # Add new fields that don't conflict
    for key in sorted(new_fields):
        if key not in existing_keys:
            new_lines.append(f"{key}: {new_fields[key]}")

    # If nothing to add, return original
    if not new_lines:
        return original_content

    # Insert after original raw lines (before closing ---)
    # First: find the position right before the closing ---
    original_delim = "---\n"
    rest = original_content[len(original_delim):]
    close_pos = rest.find("\n---")
    if close_pos == -1:
        return original_content  # safety

    prefix = original_delim
    original_body = rest[: close_pos + 1]  # includes trailing \n
    suffix = rest[close_pos + 1:]

    # Append new lines to the frontmatter body
    new_body = original_body.rstrip("\n") + "\n" + "\n".join(new_lines) + "\n"
    return prefix + new_body + suffix


def extract_conversation_id(
    fm: dict[str, object],
    filepath: Path,
) -> str | None:
    """Extract conversation_id from frontmatter or fall back to filename."""
    tid = fm.get("conversation_id") or fm.get("thread_id") or fm.get("id")
    if tid and str(tid).strip():
        return str(tid).strip()

    # Fallback: extract from filename (e.g. "thread_abc123.md" or "abc123.md")
    stem = filepath.stem
    # Remove common prefixes
    for prefix in ("thread_", "conversation_", "chat_"):
        if stem.startswith(prefix):
            return stem[len(prefix):]
    return stem  # bare stem


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: organize_threads.py <target_dir> [target_dir ...]")
        sys.exit(1)

    manifest_path = "/Users/matt/Downloads/gemini_history_export/hermes_collection_manifest.json"

    print(f"[INFO] Loading manifest: {manifest_path}")
    mapping = load_manifest(manifest_path)
    print(f"[INFO] Loaded {len(mapping)} thread mappings")

    target_dirs = [Path(d).resolve() for d in sys.argv[1:]]
    processed = 0
    moved = 0
    skipped_no_match = 0
    errors = 0

    for target_dir in target_dirs:
        if not target_dir.is_dir():
            print(f"[WARN] Not a directory, skipping: {target_dir}")
            continue

        print(f"\n[INFO] Scanning: {target_dir}")
        md_files = list(target_dir.rglob("*.md"))
        print(f"[INFO] Found {len(md_files)} .md files")

        for filepath in md_files:
            try:
                content = filepath.read_text(encoding="utf-8")
            except Exception as exc:
                print(f"  [ERROR] Cannot read {filepath.relative_to(target_dir)}: {exc}")
                errors += 1
                continue

            fm, raw_yaml, end_line = read_frontmatter(content)

            tid = extract_conversation_id(fm, filepath)
            if not tid:
                skipped_no_match += 1
                continue

            match = mapping.get(tid)
            if match is None:
                skipped_no_match += 1
                continue

            category, collection = match
            # Gracefully handle None values from manifest
            category = category or "uncategorized"
            collection = collection or "unknown"

            # Check if frontmatter already has these fields
            needs_category = "category" not in fm
            needs_collection = "collection" not in fm

            new_content = content
            if needs_category or needs_collection:
                new_fields: dict[str, str] = {}
                if needs_category:
                    new_fields["category"] = category
                if needs_collection:
                    new_fields["collection"] = collection
                new_content = write_frontmatter(content, raw_yaml, end_line, new_fields)

            # Determine destination
            dest_dir = target_dir / category / collection
            dest_path = dest_dir / filepath.name

            if dest_path == filepath:
                # Already in the right place – just update frontmatter if needed
                if new_content != content:
                    filepath.write_text(new_content, encoding="utf-8")
                    rel = filepath.relative_to(target_dir)
                    print(f"  [UPDATED] {rel}  ->  category={category}, collection={collection}")
                    processed += 1
                else:
                    # Already tagged and in correct location
                    processed += 1
                continue

            # Move into category/collection subdirectory
            dest_dir.mkdir(parents=True, exist_ok=True)
            if new_content != content:
                dest_path.write_text(new_content, encoding="utf-8")
                filepath.unlink()
            else:
                shutil.move(str(filepath), str(dest_path))

            rel_src = filepath.relative_to(target_dir)
            rel_dst = dest_path.relative_to(target_dir)
            print(f"  [MOVED] {rel_src}  ->  {rel_dst}")
            moved += 1
            processed += 1

    print("\n[DONE]")
    print(f"  Processed (matched): {processed}")
    print(f"  Of which moved:      {moved}")
    print(f"  Skipped (no match):  {skipped_no_match}")
    print(f"  Errors:              {errors}")


if __name__ == "__main__":
    main()