## Goal
Split the existing `GEMINI.md` system prompt into two modes: "triage mode" and "worker bee mode", inject them dynamically based on a UI toggle, empty out the global `GEMINI.md`, and document the triage mode clearly in `README.md`.

## Changes Made
- `src/systemPromptConfig.ts`: Created file containing `WORKER_BEE_RULES` (migrated from `GEMINI.md`) and newly defined `TRIAGE_MODE_RULES` constants.
- `src/main.ts`: Imported the config file and modified the session submission logic to read the state of the pre-triage checkbox and inject the corresponding rules dynamically into the `processedInput` buffer sent to `agy`.
- `index.html`: Added a new `<input type="checkbox" id="pre-triage-checkbox">` UI toggle next to the auto-clear context box to allow the user to easily switch between the modes.
- `GEMINI.md`: Emptied the global rules, leaving only a note directing agents and developers to the dynamic injection logic inside `systemPromptConfig.ts`.
- `README.md`: Created to detail the difference between Triage Mode and Worker Bee mode, clearly documenting the operational behavior and expectations for the agent under each scenario.

## What Worked
- Replaced the hardcoded monolithic GEMINI.md reliance with dynamic, situational prompting. 
- UI additions were placed smoothly without disrupting existing Tailwind flex layouts.

## What Didn't Work / Known Issues
- Currently, "triage mode" relies on the external agent behavior (e.g. `create_child_thread`). If the overarching framework CLI is modified, we need to ensure the system instructions still accurately match the tools available to `agy`.

## Architecture Notes
- The AI-OS architecture is purely a thin client/Tauri layer passing augmented text buffers to PTY instances. Thus, state management for system prompts correctly belongs in `main.ts` before transmission to the CLI, ensuring `agy` stays stateless and functional.
