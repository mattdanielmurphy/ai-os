I've put together the full migration plan as a markdown file. Key points at a glance:

## Core rewrite
`SKILL.md` Step 1 becomes a deterministic `code2prompt` invocation (no model call, no flash subagent) writing a single `codebase_context.md`. Step 2 becomes a single `proxima:ask_perplexity` call with that file in `files[]`, followed by a `flash_lite` subagent that reformats the raw output into `implementation_plan.md`. `planner.md` gets a matching rewrite, and the `agymcp:agy_continue` session-persistence mandate is replaced since `ask_perplexity` is stateless — follow-up passes need to re-attach prior plan + feedback as context instead.

## Biggest risks to resolve first
- **Secrets/exfiltration**: codebase content now leaves your local environment for an external service — this needs an explicit `.env`/credentials scrub in the `code2prompt` exclusion list before rollout, not after.
- **Statelessness**: confirm whether `ask_perplexity` supports any continuation, since the current design assumes a fresh reasoning pass every iteration.
- **Context ceiling**: unclear how `code2prompt` truncates when a repo exceeds Perplexity's context window — silent truncation during planning is dangerous.
- **Fidelity at the `flash_lite` formatting step**: a cheap model reformatting nuanced plan output risks dropping caveats; worth adding a verbatim-preservation instruction for the "Assumptions" and "Open Questions" sections.

The file also covers a suggested Perplexity prompt template (structured into Summary/Assumptions/Open Questions/Plan/Risks so the downstream formatter has a predictable schema), what happens to the now-dead `/planner 3.1 pro high` model-argument syntax, and a rollout sequencing checklist.