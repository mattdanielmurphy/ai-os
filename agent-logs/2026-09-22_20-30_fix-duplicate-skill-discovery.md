# Fix duplicate skill discovery

- Found 69 extra skill bundles across 68 repeated frontmatter names in `skills/`; the same tree had propagated into `~/.agents/skills`, the shared Codex/ChatGPT discovery root.
- Moved redundant bundles intact to `skills-archive/duplicate-entrypoints/`, retaining 133 unique manifests and preserving category-specific content.
- Changed `sync_skills.py` to use only repository files as inputs, snapshot source SHA-256 hashes, and move unchanged managed target files to Trash after source retirement. Modified and vendor-only target files are preserved.
- Removed `~/.gemini/antigravity/skills` from active sync and preserved its complete prior contents at `~/.gemini/antigravity/skills-legacy-backup-20260922`. Current Antigravity IDE and CLI roots remain active.
- Verified current configured discovery roots each expose one manifest per name; retained target-only vendor skills.
