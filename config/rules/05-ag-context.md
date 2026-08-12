# Project Context Maintenance Rules

You are working in a repository whose current project map is: `AG_CONTEXT.md`
These rules are mandatory for all agents to keep our repositories perfectly mapped and documented.

## 1. Read before acting
1. At the start of every task, read the root `AG_CONTEXT.md`.
2. Treat source code, executable configuration, schemas, and passing tests as stronger evidence than prose.
3. If the context file contradicts the repository, assume the context file may be stale. Investigate and correct it before proceeding.

## 2. Maintain context as part of the implementation
4. Updating `AG_CONTEXT.md` is part of completing the task, not optional documentation work.
5. **Legacy Upgrades**: If you encounter an `AG_CONTEXT.md` file that is out-of-date or uses an old format, you MUST salvage any useful, accurate information from it and completely replace the file with our new structured template format.
6. After making code changes, determine whether the change affects: project capabilities, architecture, data ownership, flows, dependencies, boundaries, decisions, or validation commands.
7. If any item is affected, update the corresponding section in `AG_CONTEXT.md` in the same change set.

## 3. Update proactively
7. Do not wait for the user to request a context update. Treat every feature, refactor, and migration as a possible context change.
8. When you discover that a prior assumption was wrong, add a correction under `Known agent misunderstandings` in the context file.
9. Record only facts supported by the current repository. Never document a planned design as if it were implemented.

## 4. Keep the file accurate and useful
10. Keep the root context file concise and high signal. Use exact paths, commands, and component names.
11. Prefer precise links to detailed documentation over duplicating it.
12. Explain non-obvious behavior and consequences, not just labels.
13. If the file becomes too large, split detailed material into linked subsystem context files rather than deleting essential facts.

## 5. Verify every context change
14. Before writing a new fact, verify it against the implementation.
15. After editing `AG_CONTEXT.md`, check that every referenced path exists, every referenced command is valid, and no section contradicts source code or tests.

## 6. Handle uncertainty explicitly
16. Do not guess architecture, ownership, dependencies, or intended behavior.
17. Distinguish clearly between implemented behavior, observed conventions, accepted decisions, workarounds, and planned behavior.

## 7. Completion gate
Before reporting any task as complete, you must confirm:
- `AG_CONTEXT.md` was reviewed for affected sections.
- Required context changes were made.
- No newly discovered misunderstanding or invariant was left undocumented.
- Your final response to the user mentions the context update (or explicitly states why no update was necessary).
