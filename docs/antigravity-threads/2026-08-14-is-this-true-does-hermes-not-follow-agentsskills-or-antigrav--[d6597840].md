---
title: "is this true? does Hermes NOT follow ~/.agents/skills? Or Antigravity? Or..."
date: "2026-08-14"
conversation_id: "d6597840-d64e-4b97-b5f9-97f42fdc0fa4"
source: "antigravity"
---

# is this true? does Hermes NOT follow ~/.agents/skills? Or Antigravity? Or...

## User

is this true?

# Exchange

---

does Hermes NOT follow ~/.agents/skills? Or Antigravity? Or Claude?
I think they all do, no?
10:58 PM

---

To answer your question directly:

No, they actually don't automatically follow ~/.agents/skills as a global directory.

Here is how the customization discovery works across these systems (especially for Hermes and Antigravity):

Global Customizations: These are loaded from ~/.gemini/config/ (or ~/.gemini/config/skills/). This is the machine-local folder that applies to all projects.
Workspace (Project) Customizations: These are loaded from .agents/ (or .agent/, _agents/) at the root of your current project (e.g., ~/projects/my-app/.agents/skills/).
So, if an agent is running inside ~/projects/my-app/, it will look at ~/projects/my-app/.agents/ and ~/.gemini/config/, but it will ignore ~/.agents/ entirely (unless your current working directory is exactly ~, making it the workspace root).

If you've been putting global skills in ~/.agents/skills/, the agents haven't been seeing them globally! They should be moved to ~/.gemini/config/skills/.

---

## Assistant

## Perplexity — 11:27 AM

Short version: the conclusion in that message is basically right, but the explanation is wrong — it wrongly implies all three tools share one config scheme (Gemini's), when in fact each tool has its own, incompatible directory convention. None of them treats `~/.agents/skills` as a recognized *global* folder.

What each tool actually does
Tool	Project/workspace skills	Global skills	Uses `.agents/`?
Claude Code	`.claude/skills/<name>/SKILL.md`	`~/.claude/skills/<name>/SKILL.md`	No — doesn't recognize `.agents` at all 
code.claude
+1

Hermes (Nous Research)	`skills/` at project root (or `skills.external_dirs` in config)	`~/.hermes/skills/`	No — its own namespace, not `.agents` 
hermes-agent.nousresearch
+2

Antigravity (Google)	`<workspace-root>/.agents/skills/`	`~/.gemini/config/skills/` (per official docs)	Yes, but only as **workspace-scoped**, not a home-directory global folder 
antigravity
+1
Where the answer goes wrong

The claim that Hermes and Claude "look at `~/.gemini/config/` and ignore `~/.agents/` entirely" is a fabrication — Claude Code has never used `.gemini` paths, and Hermes uses `~/.hermes/skills/`, a completely separate tool with its own config format. That part of the answer just pattern-matched Gemini's scheme onto unrelated tools.
hermes-agent.nousresearch
+1

The Antigravity part is closer to correct, but even there the "single global path" claim oversimplifies a real inconsistency in Google's own docs: the IDE docs say global skills go in `~/.gemini/config/skills/`, the CLI docs say `~/.gemini/antigravity-cli/skills/`, and some codelabs say `~/.gemini/antigravity/skills/` — three different documented paths for the same concept. There's also a known `.agent` vs `.agents` (singular/plural) inconsistency that's tripped people up on Reddit.
antigravity
+3

Bottom line

You were right to be suspicious. The answer isn't "no, they all secretly load from one shared Gemini config" — it's "no, because these are three separate ecosystems with three separate skill directories, and only Antigravity even recognizes an `.agents` folder, and only as project-scoped, not global." If you'd been dropping skills in `~/.agents/skills/` expecting Hermes or Claude to pick them up globally, you'd need to instead put them in `~/.hermes/skills/` (Hermes) or `~/.claude/skills/` (Claude) — Antigravity is the only one where `.agents/skills/` matters, and even then only inside a project root, with its global equivalent living under `~/.gemini/...` (exact subpath varies by which Antigravity surface you use).

---
