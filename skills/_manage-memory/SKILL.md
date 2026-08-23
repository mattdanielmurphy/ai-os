---
name: _manage-memory
description: Store, search, and prefetch durable memories via the battle-tested Mem0 engine.
---

# _manage-memory

Autonomous, battle-tested persistent memory engine for AI-OS backed by **Mem0** and local Qdrant vector search.

## Core Directives

1. **Search = Memory Signal**: Whenever an agent performs exploratory searches (file finding, grep sweeps, web lookups, config discoveries), the resolution MUST be stored in Mem0 so subsequent sessions bypass search friction.
2. **Pre-Flight Context Hydration**: Before executing non-trivial tasks, run `aios-memory prefetch "<task description>"` to surface relevant user preferences, project context, and past lessons.

## CLI Commands

### 1. Store a New Memory
```bash
aios-memory add "User prefers bun over npm/pnpm. Never use npm or pnpm." --category tooling
```

### 2. Semantic Search
```bash
aios-memory search "package manager preferences" --limit 5
```

### 3. Pre-Flight Hydration (Markdown format)
```bash
aios-memory prefetch "building the web app and running scripts"
```

### 4. List All Indexed Memories
```bash
aios-memory list
```

### 5. Ingest from Hermes `MEMORY.md`
```bash
aios-memory sync
```

### 6. Delete a Memory
```bash
aios-memory delete <memory_id>
```
