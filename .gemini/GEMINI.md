# Core Safety & Environment Rules

## Project Detection
1. **Root Rule:** A "Project Root" is the nearest ancestor containing a `.git` folder, `package.json`, `Cargo.toml`, `requirements.txt`, or `go.mod`.
2. **Exception:** The home directory (`~`) is NOT a project root, even if it contains these files.
3. **Hierarchy:** If no project root is found, default to the current working directory, but NEVER initialize a git repository in `~` or its subdirectories (unless it's a known project folder in `~/projects/`).

## Core Rules
1. **Context:** Read `AG_CONTEXT.md` at the project root before ANY work. If missing, create it at the root. Update it with durable knowledge (bullets only) after significant architectural changes.
2. **Safety:** NEVER use `rm`. ALWAYS use `mv [path] ~/.Trash/` (Exception: `node_modules`).
3. **Tooling:** ALWAYS use `bun`. NEVER use `npm` or `pnpm`.
4. **Privacy:** ALL generated GitHub repos MUST use `--private`.
5. **No Repo in ~:** NEVER initialize a git repository in the home directory (`~`).
6. **Local Temp:** NEVER use system-level `/tmp`. ALWAYS create and use a `./tmp` folder within the current project directory for temporary files or test scripts to avoid permission prompts.

## Path Migration Guardrail
- **Context**: The host machine migrated from username `matthewmurphy` to `matt`.
- **Constraint**: ALWAYS translate paths containing `/Users/matthewmurphy/` to `/Users/matt/` (or use relative paths or `~/`).

# Git Protocol Rules
- **Pre-Flight:** Agents must run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` at session start.
- **Auto-Commit:** Run `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py` for auto-commits.
