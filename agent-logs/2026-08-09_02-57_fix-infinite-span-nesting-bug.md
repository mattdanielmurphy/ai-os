# Log: Fix Infinite Span Nesting Bug
## Date: 2026-08-09
## Status: Complete

### Changes
- Refactored `gen_conversation_md.py` layout elements from `<span>` to `<div>` for document wrapper, exchange blocks, and thread banner to fix nested span issues.
- Fixed HTML stripping in `extract_user_input` so user prompts can contain raw HTML/Markdown without tag deletion.
- Updated and added unit tests in `tests/test_gen_conversation_md.py`.
