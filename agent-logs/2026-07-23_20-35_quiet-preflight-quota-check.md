## Goal
Update the preflight check (`scripts/preflight.py` and `AGENTS.md`) so that `ag-quota --all -j` evaluates quota status quietly without outputting the full quota JSON details into the context window on every turn.

## User Feedback & Decisions
- The user requested: "the preflight check doesn't need to actually show the model the details about how much quota is left on every turn".

## Changes Made
- Modified `scripts/preflight.py` to parse `ag-quota --all -j` output internally. If quota status is healthy, it outputs a single summary line (`ag-quota status: OK (Quota healthy)`). If warnings exist (<25% remaining or exhausted models), it outputs a concise warning line.
- Modified `AGENTS.md` to update the Pre-Flight Quota & Multi-Account Velocity Check rule to reflect that `preflight.py` runs `ag-quota` quietly without dumping verbose JSON details into the model context window on every turn.

## What Worked
- Tested `scripts/preflight.py` via `run_command`. Confirmed clean execution without dumping raw JSON.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Preflight script stdout is included directly in context when invoked by agents. Keeping output succinct prevents unnecessary token consumption.
