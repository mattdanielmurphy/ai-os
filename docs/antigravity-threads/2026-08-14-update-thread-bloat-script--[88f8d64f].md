---
title: "Update Thread Bloat Script"
date: "2026-08-14"
conversation_id: "88f8d64f-ee79-4edf-a544-28e2b6f99f77"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Please update `/Users/matt/projects/ai-os/scripts/check_thread_bloat.py`.

In `get_sys_prompt_tokens(project_root: Path)`:
1. Include a base system prompt overhead constant `base_system_tokens = 3500` (representing core agent identity, web app dev, planning mode, and instructions).
2. Fix skill token calculation:
Instead of reading the entire file contents of every `SKILL.md` (which caused a massive 481k phantom token overestimate), only parse the header/frontmatter of each `SKILL.md` (read first 2048 bytes, extract `name` and `description` from YAML frontmatter `description:` and `name:` fields, and calculate `estimate_tokens(f"- {name} ({sp}): {desc}\n")`). Also include builtin skills at `home / ".gemini/antigravity/builtin/skills/**/SKILL.md"`.
3. Set `mcp_tokens = 3200` (representing native tool declarations ~3000 tokens and lazy MCP tool names ~200 tokens).
4. Calculate `t_sys = base_system_tokens + rules_tokens + skills_tokens + mcp_tokens + ag_context_tokens`.
5. Update the returned `breakdown` dictionary to include `"base_system_tokens": base_system_tokens`, `"rules_tokens": rules_tokens`, `"skills_tokens": skills_tokens`, `"mcp_tokens": mcp_tokens`, `"ag_context_tokens": ag_context_tokens`.
6. In `main()`, ensure breakdown uses `.get()` with defaults:
```python

        "breakdown": {
            "sys_base_tokens": sys_breakdown.get("base_system_tokens", 0),
            "sys_rules_tokens": sys_breakdown.get("rules_tokens", 0),
            "sys_skills_tokens": sys_breakdown.get("skills_tokens", 0),
            "sys_mcp_tokens": sys_breakdown.get("mcp_tokens", 0),
            "sys_context_tokens": sys_breakdown.get("ag_context_tokens", 0),
            "R": R,
            "S": S,
            "M": M
        },
```

Use `replace_file_content` to make these edits cleanly in `/Users/matt/projects/ai-os/scripts/check_thread_bloat.py`.

</span>



<span title="Responded at 12:46am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The script `/Users/matt/projects/ai-os/scripts/check_thread_bloat.py` has been updated as requested.

### Key Changes
*   **System Prompt Overhead**: Introduced a constant `base_system_tokens = 3500`.
*   **Efficient Skill Parsing**: Replaced full file reading with YAML frontmatter extraction (reading only the first 2048 bytes) for `SKILL.md` files. This now correctly estimates tokens based on name and description rather than entire file contents.
*   **Built-in Skills**: Included support for builtin skills located at `home / ".gemini/antigravity/builtin/skills/**/SKILL.md"`.
*   **MCP Token Constants**: Set `mcp_tokens = 3200`.
*   **Breakdown Reporting**: Updated the `t_sys` calculation, the `breakdown` dictionary, and the `main()` output to safely access values using `.get()` with defaults.
The file is now ready for use.
The script `/Users/matt/projects/ai-os/scripts/check_thread_bloat.py` has been updated to remove the `yaml` dependency. It now uses standard Python library string operations to parse the YAML frontmatter of `SKILL.md` files.

</span>



</span>

</span>