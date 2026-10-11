# Morning Flow and Nudge Behavior

## Goal
After the configured minimum review count and C&H reward, automatically present remaining due cards one at a time until none remain. Keep only the latest morning nudge visible, and clear the tapped nudge when “I’m up” is selected while restoring the current stage.

## Approach
1. Inspect the morning callbacks, FSRS rating progression, reminder state, signal persistence, and focused tests.
2. Reuse the existing review progression and reminder ownership state; avoid changing non-morning review behavior.
3. Add regression coverage for automatic continuation, completion, nudge replacement, and acknowledgment cleanup.
4. Update project context and journal, run focused tests, verify runtime behavior if practical, and commit/push through the repository protocol.
