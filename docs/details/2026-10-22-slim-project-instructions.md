# Slim project instructions (2026-10-22)

## 22:55 Slimmed Everything project instructions

Asked (via coordinator): project instructions passed the 16k limit; propose a slim version under 8k, move anything missing into the Mac rules first, add a pointer-only rule, and answer whether the limit kills the one-project/one-coordinator setup.

---

### Missing rules moved

Compared the instructions I was given against `.rules/core_safety.md`, `ui_web.md`, `web_design.md`, `audio.md`, `docs/ARCHITECTURE.md` and `~/.claude/CLAUDE.md`. Not in `.rules` yet, now added:
- core_safety.md, new section "Project Instructions Stay Pointer-Only": the pointer-only rule, `/coord` prefix, long threads → HANDOFF.md, Logic (PHIL 120) study ladder.
- ui_web.md: Mantine/ready-made components, spatial continuity, no AI-slop look (only partly in web_design.md before).
- `~/.claude/CLAUDE.md` (hand-maintained, not compiled): one pointer-only line.
Ran `build_rules.py`; ai-os CLAUDE.md, GEMINI.md, Codex AGENTS.md regenerated.

---

### Slim version

`docs/coordinator/project-instructions-slim.md`, ~4.6k chars. Kept: where rules live, the pointer-only rule, short "Talking to Matt" core (cloud sessions without the Mac need it), `/coord`, full coordinator routing, cross-session essentials. Dropped as Mac-loaded: UI, scope details, code/tooling detail, secrets detail, shelved list, studying detail, music detail beyond one line.

Caveat: I worked from the instructions text in my own context (~10k). The coordinator said the live text is over 16k, so anything added after my snapshot needs checking against the slim file before applying.

---

### Limit verdict

The 16k limit doesn't break one project / one coordinator: rules live in `.rules` and memory; instructions just point there.

Undo: `git revert` this commit; re-run `build_rules.py`; remove the pointer-only line from `~/.claude/CLAUDE.md`.
