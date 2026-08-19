---
title: "What are the best practices for tracking completed tasks or bounties in an..."
date: "2026-08-14"
conversation_id: "8a7d623d-1c5e-48c4-97cd-65de39d6a4f3"
source: "antigravity"
---

# What are the best practices for tracking completed tasks or bounties in an...

## User

What are the best practices for tracking completed tasks or bounties in an automated agent system using SQLite and TypeScript? Specifically, how should we structure the schema to store both text solutions and reference URLs (like GitHub PRs) to avoid duplicate processing of the same bounty?

---

## Assistant

## Perplexity — 04:08 PM

For tracking completed bounties in an automated agent system, you’ll want a schema that enforces uniqueness on the bounty identifier itself and stores both the solution text and any reference URLs (like GitHub PRs) in a way that prevents duplicate processing.

Core schema design

Use a single `bounties` (or `tasks`) table with a unique constraint on the external bounty ID (e.g., GitHub issue URL or ID). This is the primary deduplication mechanism.


```
sql
CREATE TABLE bounties (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  
  -- External identifier (unique, prevents duplicate ingestion)
  external_id TEXT NOT NULL UNIQUE,        -- e.g., "github:12345" or full issue URL
  source TEXT NOT NULL,                    -- e.g., "github", "gitlab"
  
  -- Bounty metadata
  title TEXT NOT NULL,
  description TEXT,
  bounty_amount REAL,
  currency TEXT DEFAULT 'USD',
  
  -- Status tracking
  status TEXT NOT NULL DEFAULT 'pending',  -- pending, in_progress, completed, failed
  priority INTEGER DEFAULT 0,
  
  -- Solution storage
  solution_text TEXT,                      -- The actual answer/solution
  solution_url TEXT,                       -- Reference URL (e.g., GitHub PR)
  
  -- Processing metadata
  agent_id TEXT,                           -- Which agent processed this
  started_at TEXT,
  completed_at TEXT,
  last_error TEXT,
  
  -- Timestamps
  created_at TEXT NOT NULL DEFAULT (DATETIME('now')),
  updated_at TEXT NOT NULL DEFAULT (DATETIME('now'))
);

-- Indexes for common queries
CREATE INDEX idx_bounties_status ON bounties(status);
CREATE INDEX idx_bounties_source ON bounties(source);
CREATE INDEX idx_bounties_created_at ON bounties(created_at);
```


Key points:

`external_id TEXT NOT NULL UNIQUE` is your deduplication key. Before ingesting a new bounty, query this field. If it exists, skip or update instead of inserting.
dev
+1

`solution_url` stores the GitHub PR (or other reference) separately from `solution_text`, so you can track both the answer and where it was submitted.
bugheist

`status` supports state-machine style processing (pending → in_progress → completed/failed), which is a common pattern for task schedulers.
dev

TypeScript integration pattern

In TypeScript, define types that mirror the schema and use parameterized queries to avoid SQL injection:


```
ts
interface Bounty {
  id?: number;
  externalId: string;      // unique key
  source: string;
  title: string;
  description?: string;
  bountyAmount?: number;
  currency?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  priority?: number;
  solutionText?: string;
  solutionUrl?: string;
  agentId?: string;
  startedAt?: string;
  completedAt?: string;
  lastError?: string;
  createdAt?: string;
  updatedAt?: string;
}

// Example: insert or ignore duplicate bounties
async function upsertBounty(db: Database, bounty: Bounty) {
  const sql = `
    INSERT INTO bounties (
      external_id, source, title, description,
      bounty_amount, currency, status, priority
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(external_id) DO UPDATE SET
      title = excluded.title,
      description = excluded.description,
      bounty_amount = excluded.bounty_amount,
      updated_at = DATETIME('now')
    RETURNING id;
  `;

  return db.prepare(sql).get(
    bounty.externalId,
    bounty.source,
    bounty.title,
    bounty.description ?? null,
    bounty.bountyAmount ?? null,
    bounty.currency ?? 'USD',
    bounty.status,
    bounty.priority ?? 0
  );
}

// Mark bounty as completed with solution and PR URL
async function completeBounty(
  db: Database,
  externalId: string,
  solutionText: string,
  prUrl: string,
  agentId: string
) {
  const sql = `
    UPDATE bounties
    SET
      status = 'completed',
      solution_text = ?,
      solution_url = ?,
      agent_id = ?,
      completed_at = DATETIME('now'),
      updated_at = DATETIME('now')
    WHERE external_id = ?
  `;

  return db.prepare(sql).run(solutionText, prUrl, agentId, externalId);
}
```

Avoiding duplicate processing

To prevent an agent from re-processing the same bounty:

**Before claiming work:**
Query for `status = 'pending'` and lock via `SELECT ... FOR UPDATE` (or use a transaction with `UPDATE ... WHERE status = 'pending'` and check `changes()`).


```
ts
const claimSql = `
  UPDATE bounties
  SET status = 'in_progress',
      started_at = DATETIME('now'),
      updated_at = DATETIME('now'),
      agent_id = ?
  WHERE external_id = ?
    AND status = 'pending'
`;
const result = db.prepare(claimSql).run(agentId, externalId);
if (result.changes === 0) {
  // Already claimed or completed by another agent
  return null;
}
```


This pattern ensures only one agent can transition a given bounty from `pending` to `in_progress`.
dev
+1

**Before ingesting new bounties:**
Always check `external_id` uniqueness at the application layer as well, not just relying on the database constraint, so you can log or skip gracefully instead of hitting a constraint error.

**Idempotent completion:**
When marking as completed, use `WHERE external_id = ? AND status != 'completed'` if you want to avoid overwriting an already-completed entry accidentally.

Optional: separate references table

If a single bounty can have multiple PRs or reference URLs (e.g., multiple attempts or related PRs), normalize into a child table:


```
sql
CREATE TABLE bounty_references (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  bounty_id INTEGER NOT NULL REFERENCES bounties(id) ON DELETE CASCADE,
  url TEXT NOT NULL,
  reference_type TEXT NOT NULL,  -- 'pr', 'commit', 'discussion', etc.
  metadata TEXT,                 -- JSON for extra info
  created_at TEXT NOT NULL DEFAULT (DATETIME('now'))
);

CREATE INDEX idx_bounty_references_bounty_id ON bounty_references(bounty_id);
```


Then `bounties.solution_url` can store the primary/canonical PR, while `bounty_references` holds additional links.
medium
+1

Migration and tooling tips

Use a migration tool (e.g., `migrate`, `db-migrate`, or a simple custom script) to manage schema changes over time.
dev

Enable WAL mode for better concurrency if multiple agents write simultaneously:


```
sql
PRAGMA journal_mode = WAL;
```


Consider adding a `task_events` or `bounty_events` table for audit logging if you need to trace state transitions for debugging.
dev

This design gives you strong deduplication via `external_id`, clear separation between solution content and reference URLs, and a robust state machine for agent coordination.

---
