---
title: "Optimizing Proxima Planner Prompts"
date: "2026-08-13"
conversation_id: "fd15b41b-bd1e-46d9-a1fa-3756df089593"
source: "antigravity"
---

# Optimizing Proxima Planner Prompts

## User

I wonder for proxima planner skill, if we should just include the contents of agcontext for that project directly in the prompt just so they don't have to read it themselves. If it's mandatory reading, we might as well just include it in the prompt itself, right?

---

## Assistant

Yes, **absolutely!** Including `AG_CONTEXT.md` directly into the prompt via `generate_planner_prompt.py` makes complete sense and is a significant workflow optimization. 

### Why this is a great change:
1. **Eliminates Dependency on External Repo Indexing/Reading**: Perplexity's GitHub connector might not have indexed `AG_CONTEXT.md` immediately after a commit, or Perplexity may fail to query it during its search turn. 
2. **Guarantees Mandatory Context Availability**: Since `AG_CONTEXT.md` contains high-level architecture decisions, project constraints, conventions, and state, embedding it directly into `planner_prompt.txt` ensures Perplexity sees the project's exact ground truth upfront without spending search turns retrieving it.
3. **Zero Token Friction**: `AG_CONTEXT.md` is designed to be concise bullet points, so embedding it adds minimal overhead to the prompt while providing high-value context.

### What should be updated:
We can modify [`generate_planner_prompt.py`](file:///Users/matt/projects/ai-os/scripts/generate_planner_prompt.py) to automatically check for `AG_CONTEXT.md` in the project root (or working directory), read its contents, and append it into `planner_prompt.txt`.

For example, in [`generate_planner_prompt.py`](file:///Users/matt/projects/ai-os/scripts/generate_planner_prompt.py):

```python
# Check for AG_CONTEXT.md
ag_context_str = ""
ag_context_path = Path("./AG_CONTEXT.md")
if ag_context_path.exists():
    ag_context_str = f"\n--- AG_CONTEXT.md ---\n{ag_context_path.read_text(errors='ignore')}\n"
```

And then include `{ag_context_str}` in `prompt_content`.

Would you like me to update [`generate_planner_prompt.py`](file:///Users/matt/projects/ai-os/scripts/generate_planner_prompt.py) to automatically include `AG_CONTEXT.md`?

---
*Reference Thread Artifact: *

---

## User

yep

---

## Assistant

Stop calling tools and wait for the subagent to report back.

I've updated [`generate_planner_prompt.py`](file:///Users/matt/projects/ai-os/scripts/generate_planner_prompt.py) so that it automatically reads `AG_CONTEXT.md` (if it exists in the project root) and embeds its contents directly into `./tmp/planner_prompt.txt`.

### Summary of Changes:
- Modified [`generate_planner_prompt.py`](file:///Users/matt/projects/ai-os/scripts/generate_planner_prompt.py) to check for `./AG_CONTEXT.md` and insert its full text under a `--- AG_CONTEXT.md ---` section header in the Perplexity planner prompt.
- Ran `auto_commit.py` to push the change to remote.

Now, whenever you invoke `/proxima-planner`, Perplexity will receive the full `AG_CONTEXT.md` directly in the prompt without needing to fetch or query it separately.

---
*Reference Thread Artifact: *

---

## User

Hey, even though Planner Prompt did spit out the entire prompt with the instructions and AG context, the agent just looked at all that and extracted the user prompt and passed only that along and not the rest of AG context, etc.

---

## Assistant

Ah! Look at line 11 of [`proxima-planner.md`](file:///.gemini/config/global_workflows/proxima-planner.md) and execution instruction step 2 of [`generate_planner_prompt.py`](file:///Users/matt/projects/ai-os/scripts/generate_planner_prompt.py):

In [`proxima-planner.md`](file:///.gemini/config/global_workflows/proxima-planner.md):
> 4. **Invoke Perplexity**: Call `proxima:ask_perplexity` with the content of `./tmp/planner_prompt.txt`. Instruct Perplexity to query the GitHub connector for repository source code and documentation.

In [`generate_planner_prompt.py`](file:///Users/matt/projects/ai-os/scripts/generate_planner_prompt.py):
> `2. Call proxima:ask_perplexity with the prompt content.`

The problem is that agents reading line 11 or those instructions mentally paraphrase "call with the content" as: *"read the prompt file, extract what the user wants, and ask Perplexity that question."* They treat the wrapper text/AG context inside `planner_prompt.txt` as background meta-instructions for *themselves* rather than passing the **ENTIRE, verbatim string contents** of `planner_prompt.txt` as the `query` argument to `proxima:ask_perplexity`!

### The Fix

We need to explicitly enforce **VERBATIM PASS-THROUGH** in both places:

1. **In [`proxima-planner.md`](file:///.gemini/config/global_workflows/proxima-planner.md)**:
   Change step 4 to:
   > 4. **Invoke Perplexity**: Read the EXACT verbatim text from `./tmp/planner_prompt.txt`. Pass the entire string directly into the `query` parameter of `proxima:ask_perplexity` without summarizing, trimming, or extracting just the user request portion.

2. **In [`generate_planner_prompt.py`](file:///Users/matt/projects/ai-os/scripts/generate_planner_prompt.py)**:
   Change the output instructions to explicitly state:
   > `2. Read the entire text of ./tmp/planner_prompt.txt into a variable and pass it VERBATIM as the query parameter to proxima:ask_perplexity. Do NOT extract or pass only the user request.`

Let's update both files to enforce strict verbatim pass-through!

Stop calling tools and wait for the subagent to complete.

Good catch! Agents were reading `planner_prompt.txt` as meta-instructions for themselves, extracting just the raw user request, and passing only that to `ask_perplexity`.

### What We Fixed:

1. **Updated [`proxima-planner.md`](file:///.gemini/config/global_workflows/proxima-planner.md)**:
   - Added explicit instructions requiring the agent to read the **exact verbatim text** from `./tmp/planner_prompt.txt` and pass the entire string directly into the `query` parameter of `proxima:ask_perplexity` without summarizing, trimming, or extracting just the user request portion.

2. **Updated [`generate_planner_prompt.py`](file:///Users/matt/projects/ai-os/scripts/generate_planner_prompt.py)**:
   - Updated the stdout execution instructions printed by the script to explicitly state:
     `2. Read the entire text of ./tmp/planner_prompt.txt and pass it VERBATIM as the query parameter to proxima:ask_perplexity. Do NOT extract or pass only the user request.`

3. **Committed & Pushed**:
   - Committed the script updates via `auto_commit.py`.

From now on, agents executing `/proxima-planner` will pass the entire generated prompt string (including `AG_CONTEXT.md`, log excerpts, and repo context) verbatim into Perplexity!

---
*Reference Thread Artifact: *

---
