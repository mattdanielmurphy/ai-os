---
name: hermes-to-agy
description: "Delegate to agy with full Hermes system context (SOUL + memory) for free Antigravity quota."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [agy, delegation, quota, cheap, hermes]
    related_skills: [agy]
---

# Hermes-to-Agy Bridge

Route tasks through agy's Gemini backend (Antigravity free quota) while preserving Hermes's system context — SOUL.md identity, memory, and user profile.

## When to Use

- User wants to save API credits by using agy's free Gemini quota
- Simple questions, research tasks, or anything that doesn't need Hermes's full tool loop
- Fire-and-forget delegation where agy handles the work and returns results

## How It Works

1. `~/scripts/hermes-context-extractor.py` extracts Hermes's SOUL.md + memory into a cached text file
2. When delegating to agy, prepend that context to the user's prompt
3. Call `mcp__agymcp__agy(PROMPT=..., backend="agy")` — agy routes through Antigravity free quota
4. agy processes the request with its own tools and returns the result

## Procedure

### 1. Ensure context is fresh (run once per session)
```bash
~/.hermes/hermes-agent/venv/bin/python ~/scripts/hermes-context-extractor.py --save
```

### 2. Read the context
Use `read_file` to read `~/scripts/hermes-system-context.txt`

### 3. Delegate to agy
Call `mcp__agymcp__agy` with:
- `PROMPT`: the system context + "\n\n---\n\nUSER QUERY: " + the user's actual message
- `backend`: "agy" (uses Antigravity free quota)
- `timeout`: 120-300 depending on complexity

### 4. Process the result
- Present agy's response to the user
- Update Hermes memory if agy discovered something worth remembering
- Create/update skills if a reusable pattern emerged

## Quick Reference

```python
# Read context
context = read_file("~/scripts/hermes-system-context.txt")

# Delegate
mcp__agymcp__agy(
    PROMPT=f"{context}\n\n---\n\nUSER QUERY: {user_message}",
    backend="agy",
    timeout=120
)
```

## Pitfalls

1. **Context can go stale** — memory changes during a session. Re-run the extractor after significant memory updates.
2. **agy has its own tools** — it can't use Hermes's tools. For tasks needing Hermes-specific tools (skill_manage, session_search, etc.), handle them directly.
3. **agy's model is cheaper but different** — "Gemini 3.5 Flash (Low)" is fast and free but less capable than DeepSeek v4 Pro for complex reasoning.
4. **One-shot only** — `mcp__agymcp__agy` is synchronous one-shot. For multi-turn work, use `agy_start` + `agy_continue` with the same SESSION_ID.
5. **CWD matters** — agy inherits the working directory. Set `cd` parameter to the relevant project root for project-specific context.
