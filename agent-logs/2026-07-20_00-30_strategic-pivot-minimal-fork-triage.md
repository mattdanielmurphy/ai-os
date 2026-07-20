## Goal
Pause the frantic, multi-directional development and re-anchor on a clean architecture. The user hit a breaking point: Hermes WebUI "cancel" drops thread context, the monkey-patching approach (`aios_hermes_wrapper.py` + `sitecustomize.py`) is fragile, and the Tauri GUI is buggy. The user wants simplicity and reliability.

## User Feedback & Decisions
- User explicitly stated the current approach is "fucking exhausting and dispiriting" — too many pivots, too many broken pieces.
- User wants a **REALLY solid Claude Code UI** with a custom triage model, routing to Hermes or agy via litellm — no forking required on the model side.
- User acknowledged that even if Claude Code TUI has shortcomings (text editing/display), they'd tolerate it if the architecture is clean.
- User recognized they need BOTH: a launcher/shell wrapper AND a webview wrapper (the existing Tauri app).
- **Key decision**: User wants the benefit of Hermes (tool ecosystem, system prompts) driving agy execution, but finds the current "fake tool call" approach messy. They are open to a **minimal fork of Hermes Agent** that retains upstream merge capability.
- User wants to establish better documentation practices to track decisions and reduce the "forgetting what I decided" problem.

## Changes Made
- Created this log entry documenting the strategic conversation and architectural direction.
- (No code changes yet — this is a planning/strategy session.)

## Direction Agreed Upon

### Architecture: Minimal Fork + litellm Bridge
```
User → [Launcher Shell Wrapper]
         ├── triage_router.tier1_triage(prompt)
         ├── non-coding → cheap direct LLM response (via litellm)
         └── coding → Claude Code CLI → litellm → actual model
                               OR
                       Hermes Agent (forked) → agy provider
```

### What the Fork Changes (vs. current approach)
**Current (fragile):** Monkey-patch `interruptible_api_call` → inject fake tool_call for `agy_start` → Hermes runs it as a tool
**Proposed (clean):** Fork Hermes Agent provider selection → add agy as a real provider (not a tool) → triage routes to it directly

The fork adds ~30 lines at the provider/resolution layer instead of 190 lines of monkey-patching across two files (wrapper + sitecustomize).

### Upstream Compatibility Strategy
- Fork Hermes Agent, minimal changes (ideally 1-2 files)
- Periodically `git merge upstream/main`
- Surface area: provider router + agy provider implementation

### Immediate Next Steps (not yet started)
1. Map the exact files in Hermes Agent source that need modification
2. Identify the provider selection/resolution call chain
3. Implement the fork with triage hook
4. Fix or simplify the Tauri GUI to be a stable webview wrapper

## What Worked
- Having a calm, strategic conversation instead of another frantic patch session.
- Identifying that the monkey-patching approach has hit its maintainability limit.
- Recognizing that a minimal fork is a reasonable tradeoff for the control needed.

## What Didn't Work / Known Issues
- The Tauri GUI is "pretty much every aspect is somewhat broken or badly done" — needs overhaul or replacement.
- Heavy hermes-agent integration in the Tauri app isn't solid.
- The dual-run problem (Hermes spawns agy, agy re-runs with full Hermes system prompt) wastes tokens — the fork approach could potentially solve this by making agy the *provider* rather than a *tool*.

## Architecture Notes
- Claude Code handles Ctrl+C interrupts correctly (keeps context) — this is what broke the user on Hermes WebUI.
- litellm is the universal API translator — already in use conceptually.
- The existing `triage_router.py` classification logic is solid — should be reused as-is in the fork.
- The user's Tauri app (`/Users/matt/projects/ai-os/gui/`) wraps Google Gemini web and Hermes WebSocket — this should be simplified to just be a reliable webview container.
