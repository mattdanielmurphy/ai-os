# Web Design & Anti-Slop Policy

## Colour comes from the shared palette (Matt, 2026-10-22)
- Never invent, generate or randomise a palette per project, and never hard-code a colour from a style guide. Every colour comes from Matt's one shared master palette, by role (`~/projects/ai-os/docs/ARCHITECTURE.md` section 6). Until that palette is picked, add no new hard-coded colours.
- Every page and app is designed and contrast-checked in light and dark; light is the default, dark follows the system (`prefers-color-scheme` on the web, the system appearance in native apps).

## Permanently Banned Aesthetics ("AI Slop")
1. **Aggressive Tech Gradients:** Banned. No purple-to-pink, blue-to-violet, or neon gloss gradients on text, buttons, hero elements, or card borders.
2. **Banned hues:** no default indigo/violet accents, no generic amber/brown-orange (`amber-500`, warm mustard). **Never terracotta (Matt, 2026-10-22: "Never ever make anything this color ever again")**: no terracotta (the muted clay brown-orange LLM apps overuse, e.g. `#c96442`, `#C2502F`); orange itself is fine (Matt likes it), and don't use the word in proposals.
3. **Slop Decoration:** No unearned glassmorphism/backdrop blurs without real surface depth, no accent left-rail strips on cards, no icon toppers centered over every heading, and no monument stat numbers taking up storytelling space.
4. **Compositional Defaulting:** Never default to centered hero + 3 identical card tiles. Commit to a surface archetype before writing layout or tokens.
5. **Unsolicited Dark-Only Pages:** Never ship a page in dark mode only; light is the default and dark follows the system.

## Workflow
1. Commit to a surface archetype first (Monitor, Operate, Compare, Configure, Decide/Learn, Explore, Command/Inspect).
2. Take colours, type and components from the shared system (ARCHITECTURE.md), never from a borrowed brand's style guide.
3. Run the 10-point Slop Diagnostic before finalizing web interfaces.
