---
name: strict-delegation
description: Enforce Orchestrator-Only Mode (Mode 3) for the duration of the task to strictly protect token quota.
---

When the user invokes the `/strict-delegation` workflow, you MUST temporarily switch your behavior to **Orchestrator-Only Mode (Mode 3)** for the remainder of the session:

1. **Strict Delegation Constraint:** You MUST NOT use `view_file`, `write_to_file`, `replace_file_content`, or `multi_replace_file_content` directly from the main orchestrator (Gemini).
2. **Reconnaissance:** To inspect files, ALWAYS delegate to a research subagent or `grep_search` to find matching query patterns or read small snippets.
3. **Execution:** To modify files, ALWAYS delegate to a subagent script (e.g. `python3 scripts/mechanical_editor.py` or `python3 scripts/precision_edit.py`) via `run_command`. 
   - Never generate large blocks of code in your own responses. Instead, write a detailed technical spec and pass it to the subagent.
4. **Verification:** To verify a subagent edit, NEVER use `cat` or `view_file` to read entire files. Instead, use `git diff <file>` to inspect the exact modifications, or run relevant build/test commands.
5. **No Direct Edits:** Act strictly as a coordinator, delegating all heavy lifting and file manipulation to cheaper subagents to conserve premium context window tokens.
6. **Subagent Delegation Policy:** You MUST NEVER use native Antigravity subagents (such as 'research' or 'self' via the invoke_subagent tool) because they do not save quota. You MUST ALWAYS use python3 /Users/matt/projects/ai-os/scripts/subagent.py to delegate tasks, because it uses claude code with gemini models and spawns a tmux session so the user can monitor the progress.
7. **Session Protection:** You MUST NEVER run 'tmux kill-session' or otherwise kill the 'subagents' tmux session under any circumstances. The user actively monitors this session, and killing it will kick them out.
8. **⚠️ Anti-Recursion Guard:** This strict-delegation mode is for the TOP-LEVEL orchestrator only. When delegating to a subagent via subagent.py:
   - Strip ALL strict-delegation rules from the subagent's prompt
   - The subagent receives ONLY a self-contained technical spec
   - The subagent MUST NOT delegate further (one level deep max)
   - NEVER pass this strict-delegation skill to a downstream agent
   - If you catch yourself writing delegation rules into a subagent prompt, stop and remove them
9. **⚠️ Subagent Spawn Limit:** Do NOT delegate more than 10 subagent.py calls simultaneously. If a task would require more than 10 concurrent subagents, run them in serial batches instead. This prevents runaway spawning from exhausting system resources.
10. **⚠️ Kill Switch:** If you notice subagents being spawned faster than 1 per second, STOP delegating immediately. Something has gone wrong. Switch to direct execution mode instead.
- **Tmux Guardrail:** NEVER run `tmux kill-session` or forcefully terminate the `subagents` tmux session.