---
title: "Update Agent Postflight Rules"
date: "2026-08-14"
conversation_id: "fda0be82-5eeb-4449-b08a-1d68421c8341"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Please make the following rule updates to ensure all agents in new and existing threads execute postflight.py:

1. Update `/Users/matt/projects/ai-os/.rules/gemini_only.md`:
Add under `## Gemini / Antigravity Specific Rules`:
```markdown

## Mandatory Post-Flight Response Protocol
- **Rule:** Before concluding any turn or delivering a final response to the user, the agent MUST execute `python3 /Users/matt/projects/ai-os/scripts/postflight.py` (or pipe the response through it) to obtain live thread metrics and quota information (token count, Perplexity quota, etc.), and append the resulting `**Thread Metrics:**` block directly to the final response.
```

2. Update `/Users/matt/projects/ai-os/.rules/claude_only.md` and `/Users/matt/projects/ai-os/.rules/hermes_only.md` with the same `## Mandatory Post-Flight Response Protocol` section.

3. Update `/Users/matt/projects/ai-os/.rules/git_protocol.md`:
Under `## Auto-Commit Protocol`:
Add:
```markdown

- **Post-Flight:** Before concluding any turn or committing, agents MUST run `python3 /Users/matt/projects/ai-os/scripts/postflight.py` to retrieve and append live thread metrics and token counts to their responses.
```

4. Update `/Users/matt/projects/ai-os/scripts/preflight.py`:
In `main()` or in the steps list, ensure preflight prints:
`- Postflight: MANDATORY (Run python3 /Users/matt/projects/ai-os/scripts/postflight.py at turn end to inject thread metrics)`

5. Run `python3 /Users/matt/projects/ai-os/scripts/build_rules.py` to recompile `~/.gemini/GEMINI.md`, `CLAUDE.md`, `HERMES.md`, and `LEAF.md`.

Please execute these changes now.

</span>



<span title="Responded at 2:01am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The requested rule updates and the `preflight.py` modification have been completed and verified.

### Changes Performed:
1.  **Rule Files Updated**:
    *   Added `Mandatory Post-Flight Response Protocol` section to:
        *   `/Users/matt/projects/ai-os/.rules/gemini_only.md`
        *   `/Users/matt/projects/ai-os/.rules/claude_only.md`
        *   `/Users/matt/projects/ai-os/.rules/hermes_only.md`
    *   Added `- **Post-Flight:** ...` rule to `## Auto-Commit Protocol` in `/Users/matt/projects/ai-os/.rules/git_protocol.md`.
2.  **`preflight.py` Updated**:
    *   Injected the mandatory postflight reminder into the `preflight.py` steps list.
3.  **Compilation**:
    *   Executed `python3 /Users/matt/projects/ai-os/scripts/build_rules.py` to recompile `GEMINI.md`, `CLAUDE.md`, `HERMES.md`, and `LEAF.md`.
> [!NOTE]
> During the execution of `build_rules.py`, a `shutil.SameFileError` occurred related to skill synchronization, but the core rule files (`CLAUDE.md`, `GEMINI.md`, `HERMES.md`, `LEAF.md`) were successfully generated and updated.

</span>



</span>

</span>