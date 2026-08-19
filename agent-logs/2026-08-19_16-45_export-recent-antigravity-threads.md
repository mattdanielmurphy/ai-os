# 2026-08-19: Export Recent Antigravity Threads to Markdown

## Summary
Created `scripts/export_recent_threads.py` to harvest, decode, and structure all Antigravity and Antigravity-CLI conversation threads from the past month into standalone markdown files in `docs/antigravity-threads/`.

## Details
- Extracted conversation metadata and titles from `agyhub_summaries_proto.pb` (2,211 titles decoded from wire protobuf payload), `thread_summaries.json`, and transcript `<THREAD_NAME>` tags.
- Filtered 1,632 user conversations active within the past 31 days (since July 19, 2026).
- Exported 1,625 structured conversation markdown files with YAML frontmatter (`title`, `date`, `conversation_id`, `source`), standard user/assistant markdown sections, and normalized filenames (`YYYY-MM-DD_<slug>--[<short_id>].md`).
- Placed exports in `/Users/matt/projects/ai-os/docs/antigravity-threads/` so they can be immediately indexed, searched, and `@`-referenced across projects in the IDE.
