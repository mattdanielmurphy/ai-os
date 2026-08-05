# Agent Log: Strip thread.md Links from Generated Thread Artifacts

Implemented automated link stripping for `thread.md` and `conversation_response.md` artifact links when generating `thread.md` transcripts to remove redundant UI link clutter.

## Changes Made
- `scripts/gen_conversation_md.py`: Added `clean_agent_content(text: str) -> str` function using regex matching to remove `thread.md` and `conversation_response.md` artifact links and clean up orphan bullet points or reference prefixes (e.g. `Reference link to thread artifact:`). Applied `clean_agent_content` across `parse_exchanges`, `load_agent_response`, and `make_exchange_block`.
- `tests/test_gen_conversation_md.py`: Added `test_clean_agent_content` covering standalone links, backticked links, list items, prefixed links, and legacy `conversation_response.md` links while preserving standard code/file links. All 40 unit tests pass in `run_tests.py`.

