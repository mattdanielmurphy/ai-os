# ChatGPT Local File Links

**Date:** 2026-09-23 00:02
**Scope:** Global project-board guidance, link formatting, preflight output, and the board header

## Finding

The shared file-link formatter appended localhost Zed and Finder launch URLs to every `file:///` link. The project-board instructions and preflight output also emitted those environment-specific links, which do not work as ChatGPT's normal local-file links.

## Changes

- Updated `.rules/agent_logs.md` to require a standard absolute-path Markdown link and prohibit editor- or file-manager-specific launcher URLs.
- Changed `scripts/link_formatter.py` to preserve authored links unchanged, and updated its existing callers' expectations.
- Replaced the board's quick-action launcher links and the preflight launch URL with a standard local Markdown link.
- Added the same guidance to `AG_CONTEXT.md` and recorded the change in the development journal.
- Plugin discovery found Trello available but not installed. No plugin was connected; the current board remains the local Markdown project board.

## Verification

- Inspected all active rule, script, test, and board references to the old project-board launcher pattern; none remain.
- Generated global instructions and checked the Codex output for the new standard link policy.
- Did not run the test suite.
