---
title: "Update Flash Lite Rules"
date: "2026-08-17"
conversation_id: "790f6acc-90ce-449f-9950-0d6799a6677b"
source: "antigravity"
---

# Update Flash Lite Rules

## User

In `/Users/matt/projects/ai-os/.rules/gemini_only.md`, replace lines 16-28 with the exact following content:

```markdown
<!-- RULE:FLASH_LITE_DELEGATION -->
## Flash-Lite Edit Delegation (Antigravity Native)
- **Rule:** When running in Antigravity, the top-level orchestrator agent MUST **never write or modify files directly** using `write_to_file`, `replace_file_content`, or `multi_replace_file_content` itself. Instead, it MUST delegate ALL file creation and editing operations to a `flash_lite` subagent. The orchestrator agent MUST NOT fall back to or use `Model: "flash"`; `flash_lite` is the strictly enforced requirement.
- **Strict Concrete Instruction Mandate**: The orchestrator MUST NEVER pass broad, conceptual, or open-ended instructions to `flash_lite` subagents. `flash_lite` is a mechanical editor and cannot infer architectural intent. Every subagent prompt MUST be 100% deterministic and surgical, providing:
  1. The exact target file path(s).
  2. Precise, verbatim code blocks or complete replacement functions to insert.
  3. Explicit instructions on what lines to replace, leaving zero ambiguity or guesswork.
- **How:** To definitively prevent recursive subagent loops, the orchestrator MUST physically restrict the subagent's tools:
  1. Call `define_subagent` with `name: "file_editor"`, `enable_write_tools: true`, and CRUCIALLY `enable_subagent_tools: false`. Include a `system_prompt` explicitly telling it that it is a leaf agent and MUST edit files directly.
  2. Spawn the subagent via `invoke_subagent` using `TypeName: "file_editor"` and `Model: "flash_lite"`. Pass a fully self-contained prompt containing the exact target file path(s) and complete, ready-to-write code snippets.
  *(Note: Because `enable_subagent_tools` is false, the child agent physically lacks the `invoke_subagent` tool, breaking any recursion loop at the system level.)*
- **Exceptions** (orchestrator may edit directly):
  1. The task is **planning-only** (producing an artifact/plan with no source code changes).
  2. The user explicitly instructs the orchestrator to make edits directly (e.g. "do it yourself", "edit it directly").
  3. The edit is a single-character or trivially obvious fix (e.g. fixing a typo the user just pointed out inline), or when making one or two known edits to a SINGLE SMALL FILE.
  4. The `flash_lite` subagent fails with a 503 capacity error — fall back to writing directly rather than blocking.
<!-- /RULE:FLASH_LITE_DELEGATION -->
```

---

## Assistant

The requested updates to `/Users/matt/projects/ai-os/.rules/gemini_only.md` have been completed successfully. I have notified the parent agent.

---
