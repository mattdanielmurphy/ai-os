# Discussions.html Production-Ready Generator & Transcript Watcher Integration

## Summary
- Upgraded `scripts/discussions_html.py` to production-ready status: implemented robust inline markdown parsing, folded code block rendering (`<details class="code-fold">`), verbose agent reply summarization (`<details class="full-reply">`), graceful non-JSON/empty handling, and project root auto-detection.
- Integrated `discussions_html` directly into `scripts/watch_transcripts.py` so both `thread.md` and `Discussions.html` are rendered whenever an active conversation transcript changes.
- Tested and verified against active thread `b92d703f` and `66e632f8`.
