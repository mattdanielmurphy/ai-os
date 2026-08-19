---
title: "In `/Users/matt/projects/jules-burner/src/execute_settlement.ts`:"
date: "2026-08-10"
conversation_id: "2a7804ba-125e-4380-accd-0394b81f9924"
source: "antigravity"
---

# In `/Users/matt/projects/jules-burner/src/execute_settlement.ts`:

## User

In `/Users/matt/projects/jules-burner/src/execute_settlement.ts`:
Replace `pool.list(...)` with `pool.querySync(...)` or `pool.subscribeMany(...)`.
In `nostr-tools` v2, `SimplePool` uses `querySync(relays, filter)` to fetch events synchronously across relays.

---

## Assistant

The `pool.list()` method has been replaced with `pool.querySync()` in `/Users/matt/projects/jules-burner/src/execute_settlement.ts` to align with `nostr-tools` v2 requirements.

---
