[2026-06-29 14:55] User:
Does antigravity-cli read ~/.gemini/GEMINI.md?

Or does it read AGENTS instead?

---

[2026-06-29 14:55] Assistant:
`antigravity-cli` reads **both**, but they serve entirely different purposes and operate at different scopes.

Here is how the CLI handles your configuration and markdown context files:

1. Global Context Scope

**`~/.gemini/GEMINI.md`**: The CLI **does** read this file. It automatically loads it as your global, user-wide ruleset. Any instructions or preferences you put here will be enforced across all of your workspaces and projects.

2. Workspace / Project Scope

When you launch `antigravity-cli` inside a specific project directory, it looks for workspace-level guidance files:

**`AGENTS.md`** (or an `.agents/` directory): This is used to define, register, or configure specific subagents, project-level instructions, and agent workflows for that local workspace.

**`.antigravity.md` / `GEMINI.md`**: For local project instructions, the CLI looks for `.antigravity.md` (which is recommended). If it's not there, it checks for a project-level `GEMINI.md` for backward compatibility.

3. Core CLI Settings

If you are looking to change your actual terminal preferences, themes, or permissions, `antigravity-cli` ignores the markdown files entirely and reads a dedicated JSON config:

**`~/.gemini/antigravity-cli/settings.json`**

**Tip:** You can quickly modify your core settings or permissions without touching the files directly by running the `/config` or `/settings` slash commands right inside the CLI.
