---
title: "Please review the implementation plan I have drafted. Specifically, is this..."
date: "2026-08-14"
conversation_id: "30820624-53d8-49c4-9219-55ef2a87ee8f"
source: "antigravity"
---

# Please review the implementation plan I have drafted. Specifically, is this...

## User

Please review the implementation plan I have drafted. Specifically, is this the right approach for deepseek configuration in litellm, and is this the best way to handle token cache staleness via postflight.py?

# Unimplemented Brainstorming Ideas

This plan implements the remaining architectural ideas and rules brainstormed in the f0c0fb80 session that were dropped before they could be fully realized or added to the wiki.

## User Review Required

- **Cache-Aware Thread Handoff (Postflight)**: The thread staleness warning will be moved to `postflight.py` instead of `preflight.py`. It will append a system informational message directly to the end of the thread / agent response advising the user about the 1-hour cache expiry. This paves the way for a future response-generation tool that intercepts and formats all agent outputs.
- **LiteLLM Model Selection & Config Update**: `summarize_thread.py` will use the absolute cheapest model: `deepseek-v4-flash-low`. We will modify the local LiteLLM `config.yaml` to explicitly add `reasoning_effort` endpoints (low, medium, high) for the DeepSeek models to give us 4 distinct levels of thinking.

## Proposed Changes

---

### Global Agent Rules

Update the system guidelines so agents strictly adhere to the new protocols.

#### [MODIFY] [GEMINI.md]
- **Clickable Links Requirement (Idea 1)**: Append a rule mandating that agents MUST ALWAYS provide clickable markdown links (`file://` or `MEDIA:`) whenever referencing any file, folder, or linkable artifact, rather than emitting plain text file paths.
- **Preflight Invocation**: Update the preflight rule to pass the current conversation ID so `preflight.py` can evaluate thread staleness: `python3 /Users/matt/projects/ai-os/scripts/preflight.py --conv-id <conversation-id>`.

---

### Thread Summarization Pipeline

A lightweight background job to summarize threads and inject that context into `preflight.py`.

#### [NEW] [summarize_thread.py]
- A new script that reads a given `transcript.jsonl`.
- Extracts the first `USER_INPUT` and the final `MODEL` response (or diff).
- Prompts the LiteLLM proxy (`deepseek-v4-flash-high`) for a 2-3 sentence high-level summary and detailed summary.
- Appends the result to a global registry at `~/.gemini/antigravity/brain/thread_summaries.json`.

#### [MODIFY] [watch_transcripts.py]
- Add a background summarization hook: detect when a conversation hasn't been updated in > 5 minutes (idle) and hasn't been summarized yet, then trigger `summarize_thread.py`.

---

### Preflight Context Injection

#### [MODIFY] [preflight.py]
- **Context Injection**: Add a step to read `thread_summaries.json` and print a brief, high-level summary of the 3 most recently summarized threads directly into the preflight output banner.

### Postflight Cache-Aware Handoff

Update `postflight.py` (which runs via `auto_commit.py` or agent execution) to append the token staleness warning.

#### [MODIFY] [postflight.py]
- **Thread Staleness (Ideas 4 & 5)**: Calculate `<current-time+1hour>`. Append the following message to `thread.md` or as standard output for the agent to relay:
> "This thread will remain fresh for about an hour. After `<time>`, you should strongly consider starting a new thread to avoid unnecessary token usage."
- This serves as an initial version of the "Response Generator Tool" concept.

---

## Assistant

## Perplexity — 10:30 PM

Your overall architecture is sensible, but I would change two important assumptions: **`reasoning_effort` should usually be a request-time parameter, not four separate LiteLLM endpoints**, and a `postflight.py` warning does not itself prevent stale token/KV-cache usage. It only communicates a policy to the user or agent.

LiteLLM configuration
Model naming

`deepseek-v4-flash-low` is not necessarily a real provider model identifier. The valid model name depends on where DeepSeek is hosted:

For DeepSeek’s API, LiteLLM expects a provider-qualified model such as `deepseek/deepseek-reasoner`.

For a vLLM or other OpenAI-compatible local deployment, the model is normally configured with an `openai/` prefix and the exact name exposed by that server.

For a third-party inference provider, the provider prefix and model slug must match that provider’s catalog.

LiteLLM’s documented DeepSeek configuration uses a user-facing alias such as `deepseek-reasoner`, mapped to `deepseek/deepseek-reasoner`; the alias does not imply that a corresponding provider model exists.
docs.litellm

Therefore, use an alias like `thread-summary` or `deepseek-summary-low`, but map it to a verified backend model:


```
text
model_list:
  - model_name: thread-summary
    litellm_params:
      model: openai/deepseek-v4-flash
      api_base: http://127.0.0.1:8000/v1
      api_key: os.environ/LOCAL_LLM_API_KEY
```


If your local server exposes a different name, replace `deepseek-v4-flash` with that exact served name.

Reasoning levels

I would not create separate model entries merely to represent low, medium, and high reasoning:


```
text
# Avoid treating these as independent models unless you need separate routing,
# budgets, permissions, or observability.
deepseek-v4-flash-low
deepseek-v4-flash-medium
deepseek-v4-flash-high
```


Instead, define one model group and pass the reasoning setting from `summarize_thread.py`:


```
python
response = completion(
    model="thread-summary",
    messages=messages,
    reasoning_effort="low",
)
```


LiteLLM’s DeepSeek documentation describes `reasoning_effort` and `thinking` as request parameters. It also states that, for the documented DeepSeek reasoner integration, `low`, `medium`, and `high` all enable thinking rather than necessarily selecting three independently calibrated thinking budgets.
docs.litellm

For DeepSeek-V4-Flash served through vLLM, the backend’s native modes may instead be `Non-think`, `Think High`, and `Think Max`. vLLM’s documented serving examples also use a DeepSeek-specific reasoning parser and chat-template configuration. That means the correct parameter may depend on the serving stack:
recipes.vllm
+1

Backend	Recommended control
DeepSeek API through LiteLLM	`reasoning_effort` or `thinking`
vLLM DeepSeek-V4-Flash	Verify the server’s supported `reasoning_effort`/chat-template values
Generic OpenAI-compatible server	Pass only parameters that that server explicitly supports
Unknown third-party provider	Check its model documentation and LiteLLM provider adapter

A robust implementation should verify the behavior empirically rather than assuming that three accepted strings produce three different budgets:

Send identical short prompts with `low`, `medium`, and `high`.

Inspect whether the backend accepts the values.

Record reasoning-token usage, latency, and output quality.

Confirm that the proxy is not silently dropping the parameter.

Fail or fall back explicitly if the parameter is unsupported.

For a summarizer, I would probably use **no reasoning or low reasoning**. A thread summary generally benefits more from sufficient input coverage and a strict output schema than from expensive extended reasoning.

Summarization pipeline

The proposed pipeline is good, but the implementation should account for concurrency and malformed transcripts.

Recommended changes

Use a stable thread identifier derived from the transcript path or conversation ID.

Store `transcript_mtime`, `summarized_at`, and a content hash.

Do not mark a thread summarized solely because a registry entry exists; resummarize if the transcript hash changes.

Use a lock around `thread_summaries.json`.

Write to a temporary file and atomically rename it.

Treat malformed or partially written JSONL lines as recoverable.

Limit the transcript sent to the model by bytes or tokens.

Escape or delimit transcript content so user text cannot override the summarization instructions.

Validate the model response against a small JSON schema.

Store a model/version identifier so summaries can be regenerated after changing prompts.

Add retry and fallback behavior if the LiteLLM proxy is unavailable.

A useful registry entry would look like:


```
json
{
  "conversation_id": "abc123",
  "source_path": "/path/to/transcript.jsonl",
  "transcript_sha256": "...",
  "summarized_at": "2026-08-11T21:40:00-06:00",
  "model": "thread-summary",
  "reasoning_effort": "low",
  "summary": "Short high-level summary.",
  "details": "More detailed summary.",
  "schema_version": 1
}
```


The “idle for more than five minutes” watcher is reasonable, but avoid a race where two watcher iterations launch two summarizers. A lock file, SQLite registry, or atomic “claimed” state would be safer than checking only whether a summary currently exists.

Also consider whether the “final `MODEL` response” is sufficient. For an agentic thread, the final response may omit important work performed by tools. If available, summarize:

initial user request;

final response;

significant tool calls or file changes;

the current unresolved TODOs.

Preflight context injection

Injecting the three most recently summarized threads can work, but “most recent” should mean **recently relevant**, not merely recently summarized. Otherwise an unrelated thread summarized seconds ago may displace a highly relevant thread summarized yesterday.

A better ranking is:

Same project or workspace.

Same conversation lineage or directory.

Recent activity.

Semantic relevance to the current request.

Recency as a tie-breaker.

If you retain the three-thread limit, add a compact label and age:


```
text
Recent related thread:
[project-x / abc123 / 2h ago]
Summary: ...
```


Keep this injection strongly separated from the system instructions and label it as untrusted historical context. Historical summaries can be stale, incomplete, or contain instructions copied from user content.

Postflight cache handling

Moving the warning to `postflight.py` is not, by itself, the best way to handle cache staleness.

There are three separate concepts here:

**Provider prompt/KV caching**: whether the backend reuses tokenized or cached prefixes.

**Your thread freshness policy**: your decision that a thread should be restarted after one hour.

**User-facing notification**: how the user or agent is told about that policy.

Appending a message to `thread.md` only addresses the third—and possibly not even reliably, if the agent never relays postflight stdout. It does not invalidate a provider cache, force a new context, or guarantee reduced token usage. Some vLLM deployments explicitly configure prefix caching, so actual cache behavior belongs to the serving layer rather than `postflight.py`.
docs.vllm
+1

Better design

Have `postflight.py` write machine-readable metadata rather than append a conversational message to the transcript:


```
json
{
  "conversation_id": "abc123",
  "last_activity": "2026-08-11T21:42:00-06:00",
  "fresh_until": "2026-08-11T22:42:00-06:00",
  "warning_policy": "start-new-thread-after-fresh_until"
}
```


Then let `preflight.py` calculate the warning at invocation time:


```
text
This thread is fresh until 10:42 PM MDT. Consider starting a new thread after that time.
```


This has several advantages:

The displayed time is always current.

The warning is shown exactly when the thread is reused.

Repeated postflight runs do not pollute `thread.md`.

The timestamp is easy for other tools to consume.

You can later replace the warning with an automatic handoff or response-generation layer.

If the warning must be relayed through the agent, emit it through a clearly defined protocol channel or structured postflight artifact. Do not rely on ordinary stdout unless your execution framework guarantees that stdout is included in the next agent-visible response.

“Current time + one hour”

The one-hour value should be based on the last meaningful thread activity, not blindly on every postflight invocation. Also use timezone-aware UTC timestamps internally and convert to local time only for display. If clock skew or concurrent agents are possible, persist the source timestamp and freshness deadline together.

I would phrase the policy less absolutely:

This thread is considered fresh until `<time>`. After that, starting a new thread may reduce unnecessary context and cache-related token usage.

The current wording implies that a new thread definitely reduces token usage, which may not be true if the new thread receives a large injected summary or if the backend’s prefix cache is still reusable.

Recommended revised plan

Verify the exact DeepSeek backend model name and serving API.

Configure one LiteLLM model alias, such as `thread-summary`.

Pass `reasoning_effort` at request time only if the backend supports it.

Benchmark `low`, `medium`, and `high` before claiming they provide distinct reasoning levels.

Make summarization idempotent using a transcript hash and atomic registry updates.

Store freshness metadata separately from `thread.md`.

Have `preflight.py` display the warning dynamically.

Treat actual cache invalidation or prefix-cache behavior as a LiteLLM/backend concern.

Add tests for duplicate watcher launches, partial transcripts, proxy failure, stale summaries, timezone handling, and concurrent registry writes.

So: the **general architecture is right**, but I would keep the cache-awareness mechanism in structured metadata plus preflight, and treat `reasoning_effort` as a runtime setting rather than inventing model endpoints unless you specifically need separate aliases for routing, budgets, or permissions.

---
