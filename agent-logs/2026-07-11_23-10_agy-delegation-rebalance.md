# Agent Log

## Goal
Remove the forced "always delegate to Claude Code" behavior from agy. Change agy to handle work directly by default, only delegating to itself (agy subagents) when it makes sense for token savings. Save the extreme delegation mode as a reusable skill.

## User Feedback & Decisions
- agy should NOT always delegate to Claude Code — it costs money
- agy can and should still spawn agy subagents when it saves tokens (considering caching, thread length, required context)
- Safety rules must remain intact (no rm, pnpm only, private repos, etc.)
- The extreme delegation mode should be preserved as a skill for when it's needed
- This applies specifically to agy (Antigravity CLI), which loads AGENTS.md as its context

## Changes Made
1. **Created skill `agy-extreme-delegation`** (`~/.hermes/skills/autonomous-ai-agents/agy-extreme-delegation/SKILL.md`):
   - Contains the full old AGENTS.md delegation rules (Three-Turn Delegation Protocol, strict quota conservation, forced Claude Code/mechanical_editor.py delegation)
   - Documents how to apply (swap AGENTS.md section 10) and revert
   - Guidance on when to use vs. when not to use

2. **Updated `/Users/matt/projects/ai-os/AGENTS.md`**:
   - **Section 10**: Replaced "Strict Quota Conservation" + "Three-Turn Delegation Protocol" (which forced delegation to Claude Code) with "Token-Conscious Work" + "Self-Delegation (Preferred)"
   - **Section 11**: Softened "NEVER use grep" / "MUST use delegate_research" to "Avoid broad grep scopes; prefer agy subagent or delegate_research for large workspace scans"
   - Sections 12-19 (synchronous subagents, no heredocs, file reading rules, etc.) preserved as safety rules

3. **Updated `AG_CONTEXT.md`**:
   - Replaced "Triage Editing System" entry with new "Delegation Philosophy" summary
   - Downgraded "Three-Turn Delegation Protocol" to extreme-mode-only entry

## What Worked
- Clean separation: normal mode (self-handle + pragmatic delegation) vs extreme mode (skill with forced delegation)
- All safety rules preserved

## What Didn't Work / Known Issues
- N/A

## Architecture Notes
- agy loads AGENTS.md from its `settings.json` → `"context": ["AGENTS.md"]`
- The `agy-extreme-delegation` skill is a Hermes-level skill (not an Antigravity skill) — it documents what to change in AGENTS.md rather than being loaded directly by agy
- To fully enable extreme mode, swap section 10 content in AGENTS.md with the content from the skill