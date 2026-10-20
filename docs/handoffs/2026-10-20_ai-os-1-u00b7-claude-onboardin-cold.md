# Handoff: Quote-comment tool archival & parking (2026-10-20, cold)

## Chain
- Old thread: bc38f4be-3ebd-44fd-abb9-261596489f12 (ai-os 1 · Claude onboarding plan). Reopen with `claude --resume bc38f4be-3ebd-44fd-abb9-261596489f12`.

## Chain summary
- Matt initially wanted to scrap the Hammerspoon quote-comment module entirely.
- Realized on second thought the feature (highlight text, add comment, bundle it) is useful, just needs rethinking.
- Current module is Hammerspoon-only and Claude-composer-specific; goal is to make it platform-agnostic.
- Minimal viable version: hotkey → capture selection + prompt for comment → append to a clipboard stack (works everywhere).

## This thread
- Disabled the module: moved `~/.hammerspoon/modules/quote_comment.lua` to `~/.hammerspoon/archive/quote_comment.lua` and removed `safeRegister("modules.quote_comment")` from `init.lua:73`.
- Reload worked (expected "message port invalidated" message).
- Moved the handoff doc back to `docs/handoffs/2026-10-17_quote-comment-tool.md`.
- **Nothing committed yet.** Archived module is untracked in the Hammerspoon repo; ai-os has uncommitted changes to `Discussions.html` and `LEAF.md` (unrelated).

## Working on now
Commit the archived module in both repos and create a parking-lot entry describing the platform-agnostic goal. The module is disabled but preserved; this is a "future nice-to-have" not an urgent task.

## Keep in mind
- Matt values having the option available for later ("bound to be some situation in the future").
- The feature is useful but needs **major rethinking** for cross-platform use (not just Hammerspoon + Claude).
- Smallest viable next version: a single hotkey script that grabs selection → prompts for comment → appends both to a persistent clipboard stack. No composer injection, works everywhere.
- This is scope-creep territory; don't build it now, just document the idea so it's findable later.

## Next steps
1. Commit the archived `quote_comment.lua` in Hammerspoon (`~/.hammerspoon/`) with message like "archive: quote-comment module (disabled, reserved for platform-agnostic redesign)".
2. Commit ai-os repo changes (`docs/handoffs/` handoff doc + any other pending files).
3. Create `docs/parking-lot/2026-10-20_platform-agnostic-capture-and-comment.md`: briefly describe the goal (cross-app selection capture + comment bundling), link to the archived module, and sketch the minimal version (hotkey → clipboard stack).

## Read first
- `~/.hammerspoon/archive/quote_comment.lua` — the module to commit (unchanged, just moved).
- `docs/handoffs/2026-10-17_quote-comment-tool.md` — the original design doc (for context on what was built).
- `docs/parking-lot/` — check the format of existing entries so the new one matches.

Paste into a new thread: "Read /Users/matt/projects/ai-os/docs/handoffs/2026-10-20_ai-os-1-u00b7-claude-onboardin-cold.md and continue."
