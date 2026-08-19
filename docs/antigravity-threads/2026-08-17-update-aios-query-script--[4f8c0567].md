---
title: "Update AIOS Query Script"
date: "2026-08-17"
conversation_id: "4f8c0567-faf3-48bf-987a-d1c44a5ff96d"
source: "antigravity"
---

# Update AIOS Query Script

## User

Please update `/Users/matt/projects/ai-os/scripts/query_aios.js`:

1. Change line 178:
`let rawModel = 'gemini';` (was `'grok'`)

2. In the `isPlanMode` block (or prompt generation), add a compacted summary of the current thread history so the planner has the full conversational trajectory:
In `isPlanMode`:
Read `./tmp/` or active transcript to include a concise outline of the recent user prompts and agent responses if available.

3. Ensure line 236:
`const modelDisplay = rawModel || (provider === 'perplexity' ? 'gemini' : 'default');`

Check the rest of the file so that nowhere defaults to `'grok'`. Default is strictly `'gemini'`.

---

## Assistant

I have updated `/Users/matt/projects/ai-os/scripts/query_aios.js` according to your instructions:

1.  **Default Model:** Changed the default `rawModel` from `'grok'` to `'gemini'` (line 178).
2.  **Thread History Summary:** Updated `buildPlannerPrompt` to scan the `./tmp/` directory for recent text files (excluding `prompt` and `output` files), sort them by modification time, and include the last 1000 characters of the most recent file in the planner prompt as thread history.
3.  **Model Display Logic:** Updated the timeout error message logic (line 236) to default to `'gemini'` when the provider is `'perplexity'`.

I have verified that all references to `'grok'` as a default have been addressed.

---
