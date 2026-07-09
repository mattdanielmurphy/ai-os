## Goal
Modify the `ArrowUp` key behavior in the prompt textarea to require a second press to replace the text with history, while displaying a message on the first press. Ensure that multiline prompts are not stripped of newlines and are pasted instantly into the PTY instead of being typed character-by-character.

## Changes Made
- `src/main.ts`: Added state variable `arrowUpPressedOnce` to track the first press of the `ArrowUp` key. On the first press, the textarea's placeholder changes to prompt the user to press again. Input/blur events are attached to reset the state if they type or click away.
- `src/main.ts`: Modified the `dataToSend` payloads dispatched to `invoke('write_to_pty', ...)` to use bracketed paste sequences (`\x1b[200~` and `\x1b[201~`). This allows the terminal application to receive the full prompt text instantaneously and preserves newlines accurately.

## What Worked
- History tracking works perfectly by delaying the history fetch to the second keypress.
- Bracketed paste ensures that newlines are not mistakenly executed as empty prompts.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The terminal inputs rely heavily on bracketed paste mode support to receive blocks of text (especially multiline prompts) correctly. Without it, terminal apps may treat embedded newlines as command execution triggers.
