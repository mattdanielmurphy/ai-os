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

---

[2026-06-29 14:56] User:
When is GEMINI.md reloaded? Every new prompt?

Rules seem to be blatantly ignored

---

[2026-06-29 14:56] Assistant:
It doesn't reload on every prompt. `antigravity-cli` only parses and injects your `~/.gemini/GEMINI.md` rules into the context window **at the very start of a session** (when you boot the CLI or open a new chat instance).

If you make changes to your global markdown file mid-session, the active CLI instance won't pick them up.

If it's blatantly ignoring rules that *were* there when you started, it's usually due to one of three things:

1. Context Drift (Token Stuffing)

As a chat session grows longer, the older context (including the initial rules injected at the start) gets pushed up and can lose relevance weight. If you've been in the same terminal session for a while, the model can start suffering from "attention drift" and overlook those early system instructions.

2. A Local Project File is Overwriting It

If you have a local `.antigravity.md` or a project-level `GEMINI.md` inside your current directory, check its contents. Depending on your version, the local file's instructions can completely override or conflict with the global `~/.gemini/GEMINI.md` rules instead of merging with them.

3. Clear the Cache / Force a Reset

To force the CLI to completely re-read your global rules and clear out any cached context that might be confusing it, you don't have to restart the whole app. Just run this slash command inside the chat:

Bash

```
/reset

```


This clears the current thread's history and forces a fresh reload of your configuration and markdown rules. If it still ignores them after a `/reset`, there might be a syntax formatting issue or a conflicting directive inside your project's local `AGENTS` or `.antigravity.md` files.

---

[2026-06-29 14:56] User:
so when I type /clear it SHOULD be reloading GEMINI.md

---

[2026-06-29 14:56] Assistant:
Actually, there is a technical distinction here: `/clear` and `/reset` do two different things in the CLI.

**/clear** only clears your visible terminal screen (like the standard bash `clear` command). It keeps the exact same chat session active in the background, meaning `GEMINI.md` is **not** reloaded, and the model still remembers the entire conversation history.

**/reset** is what you want. This completely wipes the active chat memory, terminates the current session, and spins up a brand-new context window. **This is the action that forces the CLI to re-read and reload `GEMINI.md` from disk.**

If you have been using `/clear` to try and fix the rule ignoring, the model was actually still holding onto the old, stale session context. Try running `/reset` instead, and your updated rules should kick in immediately.

---

[2026-06-29 14:57] User:
I'm having my agents auto-commit. Does agy do this anyway behind the scenes?

---

[2026-06-29 14:57] Assistant:
No, `antigravity-cli` (or `agy`) does **not** auto-commit behind the scenes.

By design, it leaves version control entirely in your hands. It will modify, create, or delete files in your workspace based on your instructions, but it won't stage or commit those changes to Git on its own.

If you are seeing automated commits happen, it is coming from one of two places:

**Your custom agent instructions:** If you have explicitly told your subagents in `AGENTS.md` or `.antigravity.md` to run `git commit` after making changes, they are just following your specific workflow rules.

**An external tool/extension:** If you are running the CLI inside an IDE like Cursor or Windsurf, or alongside a tool like Cline, those environments sometimes have their own auto-commit or file-tracking behaviors enabled.

If you *want* your agents to handle this automatically, keeping it in your local project rules is the right way to go, as `agy` won't step on your toes by doing it implicitly.
