---
name: delegate-deepseek
description: Delegate well-scoped coding/verification subtasks to deepseek-v4-flash via the Claude Code CLI in a lightweight, permission-free, context-free mode. Use this to act as an orchestrator and conserve premium-model tokens for tasks like running scripts, writing throwaway test/verification code, mechanical edits, or research grunt work.
---

# Delegating to deepseek-v4-flash via Claude Code CLI

Use this skill when you want to act as an orchestrator and offload a
concrete, self-contained subtask to a cheaper/faster model instead of doing
the work yourself. `deepseek-v4-flash`, run through the `claude` CLI, is
capable enough to trust with well-defined tasks (writing verification
scripts, running tests, mechanical refactors, summarizing large outputs,
research legwork, etc).

## Command pattern

```
claude --dangerously-skip-permissions --bare --model deepseek-v4-flash --print '<task prompt>'
```

Flags, and why each one is used:

- `--dangerously-skip-permissions` — no interactive permission prompts. Only
  use this in sandboxes/local dev environments with no sensitive external
  access, never against untrusted/production systems.
- `--bare` — minimal mode: skips `CLAUDE.md`/`AGENTS.md` auto-discovery,
  hooks, LSP, plugin sync, attribution, auto-memory, and background
  prefetches. This keeps the subagent invocation cheap and fast, but it also
  means **the subagent starts with zero repo/project context**.
- `--model deepseek-v4-flash` — routes to the cheap/fast model instead of a
  premium one.
- `--print` — non-interactive, single-shot response (good for orchestration;
  no need to manage an interactive session).

Run this via the `terminal` tool with an appropriate `cd` into the relevant
project root.

## Critical rule: the prompt must be fully self-contained

Because `--bare` skips all auto-discovered context, **you must explicitly
include everything the subagent needs to know** directly in the prompt
string:

- Exact file paths (relative to the project root you `cd` into).
- Relevant code snippets or a description of the current state of the code
  if the task depends on it.
- The precise, concrete task — don't say "fix the bug", say exactly what to
  check, what commands to run, and what output format you want back.
- Any constraints (e.g. "do NOT edit files", "only report results", "write
  throwaway scripts under `./tmp/`", "don't install packages globally, use
  the existing venv at `<path>`").
- What "done" looks like and what format the final report should take (e.g.
  "report PASS/FAIL for each check with actual values").

Treat each invocation like sending a message to a competent contractor who
has never seen this codebase before and has no memory of prior turns. If a
follow-up is needed, issue a fresh `claude ... --print '...'` call with full
context again — `--print` invocations are stateless (no session continuity),
so don't assume it remembers anything from a previous call.

## Good use cases

- Writing and running a throwaway verification/test script for a specific
  function or behavior (e.g. stubbing an import, running assertions, and
  reporting pass/fail with actual values).
- Mechanical, well-specified refactors or find/replace-style edits across a
  known set of files.
- Summarizing long command output, logs, or diffs into a concise report.
- Research/lookup legwork you can clearly specify (e.g. "look up X and
  report Y").

## When NOT to use this

- Tasks requiring deep understanding of unstated project context, subtle
  architectural tradeoffs, or ambiguous requirements — those need a smarter
  model with real context, not a bare/cheap one.
- Anything touching secrets, credentials, or production systems.
- Multi-step tasks with unclear success criteria — clarify/decompose first,
  then delegate the concrete sub-steps.

## Example

```
claude --dangerously-skip-permissions --bare --model deepseek-v4-flash --print 'I need you to verify a Python regex fix in spotapi-service/main.py without a live network connection.

Context: the file has a `_normalize(s)` function... [full self-contained description of relevant code/behavior]

Task:
1. Write a throwaway script at ./tmp/test_normalize.py (do NOT modify main.py) that stubs the `fastapi` import so you can import the pure functions directly.
2. Run these specific checks: [list exact assertions]
3. Report PASS/FAIL for each with actual values, and a final summary.

Do not edit any files other than the throwaway script.'
```

After the subagent reports back, review its findings yourself before trusting
them fully — verify anything load-bearing (e.g. re-check critical logic,
re-run key commands yourself if the stakes are high) rather than blindly
propagating its claims.
