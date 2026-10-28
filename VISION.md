# ai-os vision

Big-picture direction for Matt's agent setup. Small ideas go in `IDEAS.md`.

## Our own coordinator in Claude Code (Matt, 2026-10-27)

- **Leave the Claude Projects "Everything" coordinator** for a setup we own, built on Claude Code. Reasons: Projects is a black box with no API (the Shelf can't read its thread list), it caps a coordinator chat at ~30 threads, and Matt wants full flexibility for Slub rather than a closed ecosystem.
- **Keep what Projects does well**: one place to ask for anything, trust that it routes the work to the right thread and picks the right model using several heuristics (usage pace, task size).
- **Threads just keep going.** Matt never sees a handoff. Writing into an old thread continues it in the same interface; any context refresh happens behind the scenes. If that's impossible, the fresh thread is created and opened automatically, never asked about.
- **Chain** (Matt's word): a set of threads linked through handoffs, a meta-thread.
- Research and plan: `docs/details/2026-10-27-claude-code-coordinator-migration.md`.
