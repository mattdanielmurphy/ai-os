# Agent Log: Created Unit Test Suite for Scripts & Services

## Summary
Created a zero-dependency, comprehensive unit test suite in `tests/` and root `run_tests.py` covering `gen_conversation_md.py`, `watch_transcripts.py`, `swap_turn.py`, and all non-Tauri scripts and services.

## Details
- `tests/test_gen_conversation_md.py`: `fmt_time`, `strip_html_tags`, `decode_html_entities`, `extract_user_input`, `parse_exchanges`, `load_agent_response`, `next_turn_number`, `format_prompt`, `make_exchange_block`, `generate`.
- `tests/test_watch_transcripts.py`: `get_active_convs`, `render`, `process_updates`, argument parsing.
- `tests/test_swap_turn.py`: `swap_turn_by_url`, `TurnSwapHandler` HTTP GET routes.
- `tests/test_compile_dynamic_prompt.py`: Prompt compilation, frontmatter parsing, section assembly.
- `tests/test_triage.py`: Task classification, fast path interception, model routing.
- `tests/test_subagent_handoff.py`: Subagent args, tmux session generation, thread bloat token estimation, context handoff.
- `tests/test_utils.py`: Clipboard query formatting, precision edit line matching, cost log parsing, housekeeper cleanup.
- `tests/test_agy_proxy.py`: Request transformation, tool parameter extraction, routing headers.
- `run_tests.py`: Python standard `unittest` test runner.

## Verification
Executed `python3 run_tests.py` — all 33 tests passed in 0.006s.
