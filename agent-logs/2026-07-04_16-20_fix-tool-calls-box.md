## Goal
Fix the tool calls box behavior so that it stays expanded while the agent works (i.e. as long as `pauseStatus` is `Running`) and only collapses when the agent is done and no longer working. The user also specified it should have a `max-height` of `50vh` (which was already in place).

## Changes Made
- Modified `src/main.ts` where `isThinking` is calculated. Previously, `isThinking` would switch to `false` prematurely if the agent output a step containing text (even if the agent was technically still running). 
- Updated the logic to simply set `isThinking = true` anytime `pauseStatus === 'Running'`. This ensures the UI considers the agent to be "thinking" as long as the state is `Running`.
- This change prevents the tool call box's `shouldOpen` variable from resolving to `false` during text generation, thus keeping the box fully expanded while the agent is active.
- Verified that `max-height: 50vh` was already applied to the tool calls box container (`#unified-tool-calls-list`).

## What Worked
- Replacing the restrictive `isThinking` condition fixed the premature collapse of the tool calls box.
- The box correctly collapses after the turn when `isThinking` naturally transitions back to `false` and is automatically closed via JavaScript unless hovered by the user.

## What Didn't Work / Known Issues
- `pnpm run build` failed locally due to an unrelated optional dependencies issue with `@rollup/rollup-darwin-x64` in `node_modules`.

## Architecture Notes
- The `isThinking` boolean is re-calculated on every DOM update / stream update and drives both the "Agent is thinking..." UI banner and the `<details>` expansion state of the `unified-tool-calls-box`.
- The `unified-tool-calls-box` is dynamically excluded from the generic Details state-preservation loop because it is heavily tied to the `isThinking` and `isLast` variables instead.
