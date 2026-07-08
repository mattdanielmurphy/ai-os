# Subagent Orchestration: File Swap Technique

When `ai-os` executes subagents (via `agy` or `claude`), it needs to prevent those subagents from reading global `GEMINI.md` or `CLAUDE.md` files. Otherwise, the subagents will double-load context (both your manually injected instructions *and* the global files) wasting significant tokens and possibly confusing the model.

Since neither `agy` nor `claude` have a native `--no-rules` parameter, we use the **File Swap Technique**:

## How it works:
1. Immediately prior to spawning a subagent CLI process, `ai-os` renames `~/GEMINI.md` and `~/CLAUDE.md` to `~/GEMINI.md.bak` and `~/CLAUDE.md.bak`.
2. The subagent process is launched. It looks for global files, finds none, and runs cleanly with only the injected system prompt.
3. The files are then restored.

## Critical Safety Mechanism: Time-Limited Swaps
To prevent scenarios where `ai-os` crashes while the files are swapped out—leaving your host system permanently without its global instructions—this swap must be designed with an automatic failsafe.

Because CLI agents like `agy` and `claude` only parse the `.md` files exactly ONCE during their initial boot sequence (within milliseconds), the files do NOT need to remain hidden for the entire duration of the subagent's run. 

**Implementation rule for `ai-os`:**
Whenever you swap the files, set a timer or background task to revert the swap automatically after **10 seconds**. This ensures the CLI boots without the rules, but guarantees that even if your app crashes immediately after launching the subagent, your host system's configuration is fully restored almost instantly.
