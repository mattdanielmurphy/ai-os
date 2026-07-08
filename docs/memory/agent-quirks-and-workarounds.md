# Agent Quirks and Workarounds

This file tracks ongoing behavioral issues, quirks, and anti-patterns exhibited by agents, along with the strategies and workarounds used to mitigate them.

## Issue 1: Ignoring Native Tools in Favor of Bash
- **Problem**: Agents often default to using raw bash commands (e.g., `ls -la | grep`, `cat`, `sed`) via `run_command` instead of prioritizing native, purpose-built tools like `list_dir`, `view_file`, or `grep_search`. This leads to brittle operations (like missing untracked symlinks or hitting bash escaping issues).
- **Current Mitigation**: Command interceptions (e.g., overriding shell commands or wrapping them in scripts) have been set up to block or redirect some of these behaviors. However, intercepting complex piped sequences (like `ls -la | grep ...`) remains difficult.
- **Future Work**: We need a systemic way to enforce native tool usage rules or expand command interceptions to handle pipes and complex shell strings safely.

## Issue 2: Outputting Interstitial Status Messages Before Commands/Builds
- **Problem**: Agents historically outputted status updates (e.g. "I have initiated the build process (`pnpm build`) to verify... I will update you as soon as the build finishes.") when triggering asynchronous or background actions. The user views these messages as unnecessary noise above the final output.
- **Current Mitigation**: A strict constraint has been added to `.agents/AGENTS.md` and `src/systemPromptConfig.ts` to ban interstitial status messages. Agents must execute tools/commands silently without intermediate narration and only report back once the operation or overall step is fully finished.


