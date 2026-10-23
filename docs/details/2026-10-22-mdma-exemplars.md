# MDMA exemplars reference

## 23:55 Exemplars doc written

**Asked (via coordinator):** an exemplars reference for the MDMA suite, starting with lowtechguys.com, plus a handful of top indie Mac devs; saved in ai-os, linked from the design rules, one-line pointer in `.rules`.

**Did:** read each developer's own pages (lowtechguys home, Cling, rcmd, Rogue Amoeba SoundSource, Sindre Sorhus apps, Bjango iStat Menus, CleanShot X, Panic, Cultured Code Things) and wrote `docs/EXEMPLARS.md`: an 8-point shared checklist, then one section per developer with a "Steal this" line.

---

### Who made the list and why

Low-Tech Guys first (closest match: a suite of single-purpose Mac utilities). Rogue Amoeba for menu-bar audio control (Matt's audio work). Panic for house voice. Sindre Sorhus for many tiny apps under one roof. Bjango for live numbers in the menu bar. CleanShot X for per-feature demos and a URL scheme. Things for purposeful motion. Rejected: Raycast (being replaced), Setapp-style bundles.

---

### Where it is linked

- `docs/ARCHITECTURE.md` new-app checklist item 9.
- `.rules/core_safety.md` one line after "Never invent a colour", compiled with `build_rules.py` into CLAUDE.md / GEMINI.md / Codex.

---

### Limits and risks

- Fetches return text only, so visual details (fonts, exact colours) were not captured; the doc tells agents to copy habits, not looks, anyway.
- `ARCHITECTURE.md` §6 still says "orange in general is fine", which contradicts the 2026-10-23 orange ban. Left for the palette thread.

**Undo:** revert the commit.
