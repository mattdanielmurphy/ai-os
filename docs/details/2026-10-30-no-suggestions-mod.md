# No-suggestions mod

## 14:45 Hide grey suggestions per thread

You asked for them hidden only in practice threads. Claude Code has no per-session setting, but it has a `prompt.suggest` mod hook, so no screen cover was needed. The new mod `mods/no-suggestions` drops the engine's suggestion when `~/.claude/no-suggestions/<session id>` exists. Your typing is untouched, and other threads are untouched.

Switches: `/no-suggestions` toggles; a prompt mentioning logic practice switches it on; a "Suggestions hidden" band with a Show button appears while on. The Coordinator's flag file is already in place.

Rejected: the global setting (you rely on suggestions elsewhere) and the Hammerspoon cover (a solid one hides typing).

Untested: three throwaway headless sessions produced no suggestions even with the mod off, so the actual hiding has not been seen. Validation and the unit test passed (the only validator failures are plugin-directory listing rules). The Coordinator process predates the install and must restart to load the mod. The band and command are also unseen in the Code tab.

Undo: disable `no-suggestions@ai-os-mods` in settings and delete the flag folder.
