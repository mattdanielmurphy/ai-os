# Skill synchronization

`skills/` is the source of truth for AI-OS-authored skills. Each `name` in skill frontmatter must occur once in that tree. Category copies that should not be discoverable belong in `skills-archive/`, outside `skills/`.

`scripts/sync_skills.py` copies repository files to the active runtime roots and never imports target-only skills. It records SHA-256 fingerprints for source files. When a source file is retired, a target copy moves to `~/.Trash` only when it still matches the recorded fingerprint. Older state entries and edited target/vendor files are preserved.

Active roots include `~/.agents/skills` for Codex/ChatGPT, `~/.gemini/config/skills` for Antigravity IDE, and `~/.gemini/antigravity-cli/skills` for Antigravity CLI, plus the configured Hermes, Claude, and agy roots. The legacy Antigravity IDE root `~/.gemini/antigravity/skills` is not synchronized; its prior contents are retained in a local backup folder.

Add or edit custom skills in this repository, then let `watch_skills.sh` propagate changes. Do not hand-edit installed managed copies. Vendor-only entries are retained. Check the `name` frontmatter and target paths when investigating duplicates.
