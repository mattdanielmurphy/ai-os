# Gemini Archive Ingestion — Session Detail

Ingested 13 Gemini chat threads (170 messages) into Hermes' FTS5 search database.

## Source Format

Markdown files in `~/Documents/gemini-archive/threads/` with YAML frontmatter and HTML-comment-delimited messages:

```markdown
---
source: "gemini.google.com"
conversation_id: "b1e6880670bb23a3"
title: "Gamified Jam Session Structure"
message_count: 2
---

<!-- gemini-message index=1 role=user timestamp="2026-07-08 19:43" -->
## User — 2026-07-08 19:43
message body here
<!-- /gemini-message -->

<!-- gemini-message index=2 role=assistant timestamp="2026-07-08 19:43" -->
## Gemini — 2026-07-08 19:43
response body here
<!-- /gemini-message -->
```

## Parsing Strategy

1. Extract YAML frontmatter with `^---\s*\n(.*?)\n---` regex
2. Parse `conversation_id` as `sessions.id`, `title` as `sessions.title`
3. Extract messages via `<!-- gemini-message index=N role=X timestamp="..." -->` regex
4. Strip markdown headers (`## User — ...`, `## Gemini — ...`) from message content
5. Map role `model` → `assistant` for Hermes compatibility
6. Sort messages by index for chronological order

## Ingestion Stats

| Metric | Value |
|---|---|
| Files found | 13 |
| Sessions created | 13 |
| Messages inserted | 170 |
| Errors | 0 |
| Source tag | `gemini-archive` |

## Idempotency

The script uses `conversation_id` as the `sessions.id` TEXT PK. `INSERT OR IGNORE` skips duplicates. Second run: 0 new sessions, 0 new messages.

## Rollback

```bash
cp ~/.hermes/state.db.bak.gemini-ingest ~/.hermes/state.db
```

## Files

- `~/projects/ai-os/scripts/ingest_gemini_archives.py` — the ingestion script
- `~/.hermes/state.db.bak.gemini-ingest` — backup created before first write