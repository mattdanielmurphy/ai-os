---
title: "Debug Perplexity Integration Issues"
date: "2026-08-12"
conversation_id: "446e4264-d90b-4939-b34a-2ccafb40d24c"
source: "antigravity"
---

# Debug Perplexity Integration Issues

## User

@[conversation:"Media Link Improvement Feedback"] 
debug this issue with ask_perplexity

---

## User

nevermind I can tell you sort of what happened. 
This is how the prompt begins:
"""
```md
// File: context.md
This file is a merged representation of a subset of the codebase, containing files not matching ignore patterns, combined into a single document by Repomix.

# File Summary

## Purpose
...
"""

So instead of attaching context.md, it tried to write it in the space. And that's okay as long as context.md is small enough to fit along with the prompt, but clearly that's not the case here.
So this is the fault of our tool that generates the prompt and contacts.md for the agent to then run ask_perplexity

---

## Assistant

I've found the root of the problem and implemented two fixes to prevent this from happening:

1. **Reordered the Prompt Structure in Proxima**: I modified the `buildMessageWithFiles` helper function in the Proxima MCP server (`/Users/matt/projects/external/Proxima/src/mcp/helpers.js`). Previously, it was appending your actual question/prompt to the *very bottom* of the context files. If the context was too large and the Perplexity API truncated the input, the question got chopped off completely, which is why Perplexity complained it didn't see a task. Now, the prompt is placed at the **top** before the context files.

2. **Lowered the Token Limit**: I updated the `generate_planner_prompt.py` script (`/Users/matt/projects/ai-os/scripts/generate_planner_prompt.py`) to reduce the hard limit for Repomix context size. It was previously allowing up to 100,000 tokens, which is too massive for Perplexity to process reliably via the API without choking or truncating. I've lowered the limit to **30,000 tokens**. If the codebase is larger than this, the agent will now be forced to use the `--include` flag to manually narrow down the context scope before calling Perplexity.

This should ensure that `proxima:ask_perplexity` always receives a digestable amount of context and that the core instruction is never truncated out of the prompt!

---

## User

I don't think that's a reasonable check. So the 100,000 token thing is just to let the agent know when there's a huge amount of context and whether we need to be sending all that to perplexity. Now we need another limit, which is a character limit, which is the prompt plus the characters in the context.md. Does that exceed the perplexity prompt input? If it does, then we need context.md. If it fits, then we can put it all in the chat and save ourselves a file upload quota hit.

---

## User

We should test here actually, let's test a few different values and we can see if they get cut off or not

---

## Assistant

I've just written a test script that's currently running in the background. It sends increasing lengths of text (10,000, 20,000, 30,000, and 40,000 characters) filled with filler text to Perplexity via Proxima, and attempts to see at what point Perplexity fails to echo back the secret keyword at the very end of the prompt.

We'll find out exactly where the character threshold is as soon as the test finishes! I'll report back with the results.

---

## User

clearly that test failed miserably.
I figured it out on my own. The limit is 40,000 characters.
You know what, I just thought of a good idea that we need to add to the docs. We only have 50 file uploads per week, which severely limits our ability to use Perplexity for this use case, since quite often we'll be exceeding the 40,000 character limit just to give Perplexity the needed context. However, what we could do is, if we're out of file uploads, and we can check that by querying the Perplexity API, what we should then do is break it into multiple prompts and just send them in succession. At the start of the first prompt, we'll explain that we're sending the context in batches, and then obviously at the end of the last prompt we'll say okay go ahead and start working on this.

---

## Assistant

That's brilliant! 40,000 characters is right around 10,000-12,000 tokens, which definitely makes sense for the hard cutoff on manual input, especially if file uploads are heavily limited.

I've fully integrated this logic across our setup so that we handle context dynamically and gracefully:

1. **Updated the Docs (`/planner` Workflow)**: I've added a note to `/Users/matt/.gemini/config/global_workflows/planner.md` explaining the strict 40k character limit for text prompts and the 50/week quota for file uploads. It now explicitly instructs agents to fall back to batching context over multiple prompts if the character limit is exceeded AND the file upload quota is exhausted.

2. **Updated the Script (`generate_planner_prompt.py`)**: The script now actively calculates the exact character length of the user request plus the context.
   - If it's **under 40k chars**, the script explicitly instructs the agent *not* to use a file upload to save your quota, and tells it to pass the context in the text payload instead.
   - If it's **over 40k chars**, the script warns the agent that the limit is exceeded, instructs it to use a file upload, AND provides your alternative fallback (the batching method) in case it discovers the upload limit has been hit.
   - I also restored the 100,000-token sanity check limit to prevent it from dumping completely unbounded amounts of context onto Perplexity.

This creates a bulletproof sequence that maximizes your file upload quota while ensuring Perplexity never chokes on truncated data!

---
