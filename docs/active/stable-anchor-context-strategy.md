# Stable Anchor + Volatile Append Context Strategy

If you want the most robust, set-and-forget architecture that maximizes savings without requiring a PhD in memory management, you need to move away from dumping the raw codebase into the prompt.

The most effective pattern for agentic development right now is the **Stable Anchor + Volatile Append** strategy. It elegantly sidesteps the issue of codebase edits busting your cache.

Here is exactly how you structure it.

### The "Stable Anchor" Architecture

Instead of treating your codebase as one massive block of text, you split it into two tiers of memory: the structural map (which rarely changes) and the active files (which change constantly).

Your prompt construction pipeline should build every request in this exact, strict order:

**1. The System Instructions (The Brain)**
Your persona, output constraints, and tool definitions. This is completely static.

**2. The Repo Map (The Stable Anchor)**
This is a highly compressed, text-based map of your entire project. You can generate this using a tool like `ctags` or a simple script that outputs a tree view of your directory, class names, and function signatures—but *no implementation logic*.

* *Why this works:* A repo map of a massive project is usually only 5,000 to 15,000 tokens. It gives the agent perfect spatial awareness of the architecture. Because you aren't changing file structures or renaming core classes every five minutes, this heavy block remains identical across almost every call, giving you a near-permanent cache hit.

**3. The Active Files (The Volatile Memory)**
This is where you inject the full raw text of the 1, 2, or 3 specific files the agent actually needs to look at or modify right now.

* *Why this works:* If the agent makes a substantial edit to `api_router.js`, it doesn't bust the cache for your entire project. It only changes the token sequence *after* the heavy Stable Anchor.

**4. The User Task (The Append)**
Your specific instructions or the next conversational turn.

### Why This is the Most Robust Solution

This architecture solves the exact problem regarding edits.

If you feed the model the raw codebase linearly (A to Z) and edit `auth.ts` (near the beginning), you instantly destroy the cache for every file that comes after it.

With the Repo Map strategy, your heavy context sits safely at the front. The agent always knows where everything is, and you only pay the premium, un-cached token price for the specific files you are currently modifying. It keeps the context window tight, which prevents the LLM from getting confused by 80,000 tokens of irrelevant code, while slashing your quota usage.

### Strategic Implementation Notes

If we were to build the script to generate that Repo Map dynamically, the most lightweight tools to integrate into our current launchd/git-sync workflow are:
1. `ctags` (universal-ctags) for structural extraction.
2. Lightweight parser scripts (e.g. tree-sitter or custom python scripts) that run on git hooks or launchd to compile the signature-only map.
