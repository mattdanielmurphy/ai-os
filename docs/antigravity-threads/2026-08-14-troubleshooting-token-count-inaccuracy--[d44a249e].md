---
title: "Troubleshooting Token Count Inaccuracy"
date: "2026-08-14"
conversation_id: "d44a249e-af08-4ea4-a399-60ace2036c99"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

We have to make sure that we handle this as well:
Perplexity's response started with this:
```

I pulled the repo structure via GitHub, but the content-retrieval call for individual files (postflight.py, preflight.py, bin/ai-os) only returned file metadata/SHA — the connector wouldn't surface the raw text of this private repo through get_file_contents or raw URLs (both blocked by fetch_url auth, and GitHub code search doesn't index private repos). So I can't quote your actual lines. Below is the architectural diagnosis and implementation plan based on what's confirmed from AG_CONTEXT.md and the repo's file topology (scripts/postflight.py — 1.4KB, scripts/postflight_async.py — 2.6KB, scripts/check_thread_bloat.py, scripts/agent_tokens.py, bin/ai-os — 4KB orchestrator entrypoint). If you paste the actual postflight.py + the call-site in bin/ai-os, I'll give you an exact patch.

```

That should result in the agent telling me that it didn't work and that we have to... Actually, the agent should try again once on its own and if it doesn't work then it should stop and say, "I'm having trouble with the Ask Perplexity Tool."
```

</span>



<span title="Responded at 12:51am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

I have updated the `/proxima-planner` workflow with the automated single-retry and escalation protocol:

### Updated Protocol in [`proxima-planner.md`](file:///Users/matt/.gemini/config/global_workflows/proxima-planner.md) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/config/global_workflows/proxima-planner.md)
1. **Content Retrieval Failure Detection**:
   - Inspect Perplexity's response for phrases indicating private repo or connector retrieval failure (e.g., *"connector wouldn't surface raw text"*, *"only returned file metadata/SHA"*, *"blocked by fetch_url auth"*, *"If you paste the actual..."*, *"I can't quote your actual lines"*).
2. **Automatic 1-Time Retry**:
   - If Perplexity could not read the file contents through the connector, the agent will automatically retry **once** by passing the relevant local file path(s) directly into the `files` parameter:
     ```python
     proxima:ask_perplexity(message=..., files=[path1, path2, ...])
     ```
3. **Strict Stop & Escalation**:
   - If the retry also fails or encounters errors, the agent MUST immediately stop without guessing code or falling back to manual planning, and notify you:
     > *"I'm having trouble with the Ask Perplexity Tool."*
**Thread Metrics:**
- Total Tokens: 67k (source: estimated)
- Cache Expiry: 19:52 MDT (59m left)
- Financial Rotation: 67k / Breakeven 370k (Status: OK)
- Perplexity Quota: 107 Pro remaining, 20 Research remaining

</span>



</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

For proxima_planner, we want to make sure we're telling perplexity to use the GitHub connector to read MY repo `repo name` rather than just saying " look at the repository mattdanielmurphy/repo-name" because it doesn't know that it can read private files, etc.

</span>



<span title="Responded at 12:48am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

I have updated the planner prompt generator and workflow instructions to ensure Perplexity explicitly uses its authenticated GitHub connector to read private repositories:

### Summary of Changes
1. **[`scripts/generate_planner_prompt.py`](file:///Users/matt/projects/ai-os/scripts/generate_planner_prompt.py) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/generate_planner_prompt.py)**:
   - Replaced the generic `"Target GitHub Repository: ..."` line with an explicit instruction:
     ```markdown
     --- GitHub Connector Context ---
     Target Private Repository: '<repo_name>'
     IMPORTANT: You have access to my authenticated GitHub account via your GitHub connector. Please use your GitHub connector to directly read, search, and inspect the codebase, files, and documentation in my repository '<repo_name>' (including private files and configs) as needed to construct this plan.
     ```
   - Corrected the tool parameter guidance in execution instructions to reference `message` instead of `query` for `proxima:ask_perplexity`.
2. **[`~/.gemini/config/global_workflows/proxima-planner.md`](file:///Users/matt/.gemini/config/global_workflows/proxima-planner.md) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/config/global_workflows/proxima-planner.md)**:
   - Updated Step 4 to explicitly specify that Perplexity should use its authenticated GitHub connector to inspect private repository files and documentation.
**Thread Metrics:**
- Total Tokens: 59k (source: estimated)
- Perplexity Quota: 108 Pro remaining, 20 Research remaining

</span>



</span>

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

@[conversation:"Thread Management Optimization Strategy"] our injected estimate of the thread size is wildly, insanely off. I just started this thread and it's saying it's 518,000 tokens. There is no point If it's not quite accurate.

</span>



<span title="Responded at 12:45am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

### Root Cause & Fix
The 518,000 token figure was caused by a major overestimate in `scripts/check_thread_bloat.py`:
1. **The Culprit (`481,827` phantom tokens)**: The script was reading and token-counting the entire markdown body of all ~200 `SKILL.md` files across the config and plugins folders.
   - In reality, Antigravity **never** loads full skill bodies into the system prompt; it only injects a lightweight list of `- name (path): description` (~10k tokens total).
2. **MCP Schemas (`15,855` tokens)**: The script was reading every single lazy-tool JSON schema file on disk. Lazy MCP tools are only listed by name in the system prompt.
3. **The Fix**:
   - Updated `get_sys_prompt_tokens()` in [`check_thread_bloat.py`](file:///Users/matt/projects/ai-os/scripts/check_thread_bloat.py) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/check_thread_bloat.py) to parse only skill YAML frontmatter headers (`name` + `description`), mirroring the actual injected `<skills>` block.
   - Set accurate token baselines for system prompt overhead (~3.5k tokens) and native/lazy MCP tool declarations (~3.2k tokens).

### Verified Result
- **System Prompt Overhead (`t_sys`)**: Corrected from **507,892** tokens down to **26,881** tokens.
- **Fresh/Current Thread Size**: Now accurately reports **~44k - 46k tokens** (system prefix + transcript history).
**Thread Metrics:**
- Total Tokens: 46k (source: estimated)
- Perplexity Quota: 108 Pro remaining, 20 Research remaining

</span>



</span>

</span>