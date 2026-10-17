---
name: hermes-database-internals
description: >-
  Hermes Agent's SQLite database architecture — schema layout, FTS5 dual-tokenizer
  search, trigger-based index sync, and the pattern for safely ingesting external
  data into state.db.
---

# Hermes Database Internals

Hermes stores all conversation history and search indexes in a single SQLite database at `~/.hermes/state.db`. This skill documents how it's structured and how to safely interact with it.

## Schema Map

### `sessions` table (PK = `id TEXT`)
One row per conversation. Key columns:

| Column | Type | Notes |
|---|---|---|
| `id` | TEXT PK | `"YYYYMMDD_HHMM_random"` style for Hermes-native sessions, or any unique string for ingested ones |
| `source` | TEXT | Origin: `"cli"`, `"desktop"`, `"photon"`, or custom (e.g. `"gemini-archive"`) |
| `title` | TEXT | Has a **partial unique index** (`UNIQUE INDEX idx_sessions_title_unique ON sessions(title) WHERE title IS NOT NULL`) — can set to NULL to avoid collision |
| `started_at` | REAL | Unix epoch (seconds) |
| `message_count` | INTEGER | Denormalized count |
| `model` | TEXT | Model identifier |
| `ended_at` | REAL | Optional session end time |

Other columns (`input_tokens`, `output_tokens`, `cost_*`, etc.) can be left NULL when ingesting external data.

### `messages` table (PK = `id INTEGER AUTOINCREMENT`)
One row per message in a conversation.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `session_id` | TEXT | FK → `sessions.id` (indexed jointly with `timestamp`) |
| `role` | TEXT | `"user"`, `"assistant"`, or `"system"` |
| `content` | TEXT | Message body — indexed by FTS5 |
| `timestamp` | REAL | Unix epoch |
| `active` | INTEGER | Default `1` — set to `0` to soft-delete from search |

Other columns (`tool_call_id`, `tool_calls`, `reasoning`, etc.) are for Hermes-native operation and can be NULL.

## FTS5 Search Architecture

Two virtual tables provide full-text search, **auto-populated by triggers** on the `messages` table:

### `messages_fts` — keyword search
- Columns indexed: `content`, `tool_name`, `tool_calls` (concatenated with spaces)
- Trigger: `messages_fts_insert` fires `AFTER INSERT` on `messages`
- Search: `SELECT ... FROM messages_fts WHERE messages_fts MATCH 'keyword'`
- Use: exact term matching, quoted phrases, boolean operators

### `messages_fts_trigram` — fuzzy/trigram search
- Tokenizer: `trigram` — matches substrings within words
- Trigger: `messages_fts_trigram_insert` (parallel trigger)
- Search: `SELECT ... FROM messages_fts_trigram WHERE messages_fts_trigram MATCH 'token'`
- Use: partial matches, typo-tolerant, prefix search without `*`

### Trigger behavior
- `AFTER INSERT`: inserts into BOTH FTS tables automatically
- `AFTER UPDATE`: deletes old FTS row, inserts new (full re-index of the row)
- `AFTER DELETE`: removes FTS row

This means **you only insert into the `messages` table** — the FTS indexes stay in sync automatically.

## Safe Ingestion Pattern

When ingesting external data into Hermes' state.db:

```python
# 1. Back up first
import shutil
shutil.copy2(str(state_db_path), str(state_db_path.with_suffix(".db.bak.<label>")))

# 2. Connect with WAL mode for concurrent read safety
conn = sqlite3.connect(str(state_db_path))
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=OFF")  # bulk insert speed

# 3. INSERT OR IGNORE for idempotent session creation
conn.execute(
    "INSERT OR IGNORE INTO sessions (id, source, title, started_at) VALUES (?, ?, ?, ?)",
    (session_id, source_name, title, timestamp),
)

# 4. Insert messages — triggers auto-populate FTS5
conn.execute(
    "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
    (session_id, role, content, ts),
)

# 5. Commit
conn.commit()
conn.close()
```

### Key constraints to respect
- `sessions.id` is the only dedup key — use a deterministic ID (e.g. external conversation_id) for idempotency
- `idx_sessions_title_unique` is a **partial unique index** (`WHERE title IS NOT NULL`) — set title to NULL to avoid collision with other null-title entries
- `messages.id` auto-increments — never set it manually
- Don't touch FTS virtual tables directly; insert into `messages` and let triggers handle them

## References

- `references/gemini-archive-ingestion.md` — full walkthrough of ingesting Gemini chat archives
- Hermes DB path: `~/.hermes/state.db`
- Schema dump: `sqlite3 ~/.hermes/state.db ".schema"`