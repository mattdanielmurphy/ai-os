---
name: workspace-identity
description: Matt's role, core projects, tooling constraints, and absolute knowledge routing paths
metadata:
  type: user
---

# Workspace Identity

**User:** Matt — CS student and drummer.

**Core Focus:** Self-studying Calculus. Tends to procrastinate; keep tasks atomic and immediately actionable to maintain momentum.

## Active Projects

- **ai-os** — This harness (`/Users/matthewmurphy/projects/ai-os/`)
- **CockBand** — Drum/bass Rocksmith-style clone
- **StudyEngine** — PencilKit/LaTeX note-taking app
- **Piano OS** — Tauri/Rust MIDI platform

## Tooling

- **Package manager:** `pnpm` exclusively. Never use `npm` or `yarn`.

## Absolute Knowledge Routing

These override any native Claude memory or local `MEMORY.md` interpretations:

- **Personal/User Notes:** Always route to the iCloud Obsidian vault at:
  `/Users/matthewmurphy/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/`
  This is the sole source and destination for anything called "notes", "personal notes", "recent notes", "my notes", or "saved notes".

- **Session Engineering Logs:** Always write to:
  `/Users/matthewmurphy/projects/ai-os/.agent-logs/`

## Related

See [[claude-md-override]] for how CLAUDE.md enforces these routes over native memory.

**Why:** Matt has multiple active projects and a clear knowledge routing preference (iCloud Obsidian for personal notes, local .agent-logs for engineering logs). Atomic, actionable tasks overcome procrastination.

**How to apply:** Before any operation involving "notes", verify the destination against the Obsidian vault path. Keep task decomposition shallow and immediately executable. Default to `pnpm` for all package operations.