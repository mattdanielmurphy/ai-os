# Keep Matt and Tyler in sync on Slub (2026-10-26)

## 19:45 One easy way to stop drifting apart

Matt asked (via the coordinator, before a call with Tyler): how to keep both of them in the loop on Slub so they don't build the same idea separately, given their systems already differ. Full merge comes later.

---

### What was already planned

- The Oct 23 thread planned a private `slub-utils` monorepo with Tyler as a collaborator (plan in `docs/details/2026-10-23-slub-utils-monorepo.md`). It was never created: `mattdanielmurphy/slub-utils` does not exist on GitHub today.
- The drift is real: Tyler's `tvresync` clashed with Matt's TV Re-sync (both on ⌃⌥R), and Tyler built `tvwake` on his own.
- The monorepo is a few hours of restructuring the live Hammerspoon suite, so it isn't a "before the call" fix.

---

### Recommended: shared slub-hq repo

A tiny private GitHub repo (`slub-hq`) with Tyler as a collaborator, holding:
- `NOW.md`: one line per thing either of you is building (who, what, date). Claude adds a line when work starts and removes it when done.
- `IDEAS.md`: Slub ideas (e.g. the walking-tour app), so an idea is visible before anyone builds it.
- `CLAUDE.md`: the shared rule, "before starting any Slub app or utility, pull slub-hq and check NOW.md and IDEAS.md; if it's there, ask first."

Why: both Claudes can read and write a repo from Code or Projects with no new tools, and it takes about 10 minutes. It later becomes the home of the shared rules when you merge systems.

---

### Other options

- Shared Linear team "Slub": nicer board and phone app, but Tyler needs a Linear account and his Claude needs the Linear connector.
- Build the monorepo now: solves code drift too, but hours of work and risky to the live suite; do it after the call.
- Rejected: a group chat or doc. Agents won't check it on their own, which is the whole problem.

---

### Projects vs your own Claude Code system

- The shared repo works the same whether you stay in Projects or move to plain Claude Code, so this choice doesn't block syncing with Tyler.
- If you both run Claude Code, the `CLAUDE.md` in slub-hq becomes a shared rulebook both agents load, the first real step toward one shared system.
- Untested: whether Tyler's Claude setup will reliably follow the rule; worth checking once on his Mac.

---

### Not done yet

Nothing created. Making the repo and inviting Tyler is an outward action, so it waits for Matt's 👍. Undo: archive the repo.
