---
name: obsidian-notes
description: Route all note operations to Matt's iCloud Obsidian vault. Read, search, create, and edit notes with proper naming conventions.
version: 1.1.0
metadata:
  hermes:
    tags: [obsidian, notes, note-taking, knowledge-routing]
---

# Obsidian Notes — iCloud Vault Routing

All "notes", "personal notes", "my notes", "saved notes", **"ideas"**, **"brainstorms"**, **"concepts"**, and **"ramblings"** must route to Matt's iCloud Obsidian vault. This includes when the user says "add to [project] docs: a new note, an idea" — the routing is by content type (note/idea), not by whether they mentioned a project directory. This skill encodes the vault path, naming conventions, and operational patterns.

## Vault Path

```
/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/
```

This is a Git-tracked Obsidian vault synced via iCloud. Use `read_file`, `write_file`, `search_files`, and `patch` directly — no wrapper needed.

## Note Naming Convention

- Use **human-readable filenames** derived from the note's content/title
- Good: `Space Facts 🚀.md`, `Recipe Ideas.md`, `Calculus Derivative Rules.md`
- Bad: `User_Note_2026-07-10_143052.md`, `note_1.md`
- Emoji in filenames is fine (macOS supports it)

## Creating a Note

```bash
# Use write_file directly
write_file(path="/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/<Category>/<Title>.md", content="...")
```

After creating, always provide a clickable `file://` link:
```
file:///Users/matt/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/Personal/<Category>/<Title>.md
```

## Vault Structure

Key directories observed:
- `School/` — Academic notes (calculus, history, science)
- `Financial/` — Financial planning
- `Development/` — Dev-related notes (e.g., Personal AI System)
- `Ongoing/` — Active lists and projects (Watch List, grant applications)
- Root-level notes also exist

When unsure where to place a note, create it at the vault root and let Matt organize it.

## Searching the Vault

```bash
# Search for content
search_files(pattern="search term", path="/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/", target="content")

# Find files by name
search_files(pattern="*.md", path="/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/", target="files")
```

## Reading Notes

Use `read_file` directly — the vault is plain Markdown:
```bash
read_file(path="/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/<Category>/<Note>.md")
```

## The Native Obsidian Skill

A bundled `obsidian` skill exists for general Obsidian vault operations. Load it with `skill_view(name='obsidian')` for additional Obsidian-specific workflows (templates, daily notes, dataview queries). This skill (`obsidian-notes`) focuses specifically on Matt's vault routing and naming conventions.

## Pitfalls

- **Do not route notes to a project docs directory.** Even when the user says "add to [project] docs: a new note, an idea", the correct destination is the Obsidian vault, not `~/projects/<name>/docs/`. The content type (note/idea) determines the target, not the directory mentioned in passing.
- **Do not delete and recreate notes in a panic.** If a note was placed in the wrong location, move it with `mv [src] [dst]` — never delete a note the user can see then recreate it. The user will see it vanish and assume their work is lost.
- **Do not run auto-commit or git operations on the vault.** The vault is iCloud-synced, not a git-managed ai-os project. There is nothing to commit when creating notes here.
