# UI options, a design rule, and a Figma mixer plugin

## 23:00 Nine options vs one, a draft rule, and a plugin plan

Matt asked three things: whether asking an agent for 9 UI options gives weaker designs than asking for 1, a global rule for how agents approach new UI (show options first, follow a named reference style), and a plan for a Figma "UI mixer" plugin. There is a project freeze, so nothing is built yet.

---

### Nine in one go is weaker

Asking one agent for 9 options in one reply does make each option weaker, for two reasons:

- **Attention is split.** Each option gets about a ninth of the care: fewer real details, more placeholder thinking.
- **They collapse into each other.** One model in one reply shares the same defaults, so you get 2 or 3 real ideas and 6 small variations (a colour swap, a radius change). It feels like freedom but mostly fills slots.

Asking for 1 has the opposite problem: the agent picks the safest, most default design (often the stock Claude look) and you have nothing to compare it to.

What I rejected: "more options is always better" (true only if they are actually different) and "one polished option" (no comparison, no mixing).

---

### Ask for four different directions

Recommendation: **3 or 4 directions, each made separately, each with its own forced brief.** For example: one strictly in the named reference style, one minimal, one bold, one borrowed from an exemplar in `docs/EXEMPLARS.md`. Made separately means a separate agent or call per direction, so none anchors on the others. That gives real variety *and* full care per option. Then mix the pieces you like in the UI Mixer, instead of asking for a round 2.

If you want 9, the same rule applies: 9 separate agents, one brief each. It costs more usage but the options are genuinely different.

---

### Draft rule for new UI

Proposed text for `.rules/core_safety.md` (next to rule 1m), saved only after Matt's 👍:

> **1o. Show options before building UI, and match a named style (Matt, 2026-10-25)**: before building any new UI or redesign (an app screen, a port, a page, a HUD), agents show options first and write app code only after Matt picks.
> - **Reference style first.** If Matt named a style to match ("like the explainer reel", "hairline like X"), restate it at the top of the plan as a short list of its concrete traits (fonts, line weights, colours by role, spacing, controls), and every option stays inside that style. Before shipping, compare the build side by side with the reference and fix any trait that drifted.
> - **Options as pictures, not prose.** 3 or 4 directions, each made separately with its own brief so they don't copy each other, shown as Figma boards or quick renders with the same real content, light and dark.
> - **Then mix, don't redo.** If he likes pieces of several, build a UI Mixer subject (rule 1m) instead of another round.
> - **Skip for small tweaks** (a colour, a spacing fix, a bug) and when he says "just build it".
> - Why: the Glass TV Android port ignored his ask to match the explainer reel's hairline style, and he only saw it once it was built.

What I rejected: forcing options for every UI change (too slow for small fixes, hence the skip line), and a fixed count of 9 (see above).

---

### Figma mixer plugin plan

Goal: agents generate many designs into one Figma file; a plugin panel lets Matt mix and match colours, fonts and layout pieces across them, like the web UI Mixer and the Tweaks knobs panel, and copy the result out as settings.

**Existing tools first.** Figma already does part of this natively: *variable modes* swap a whole palette in one click, and *component variants* swap a piece (header style A/B/C). The plugin's job is to put those behind one simple panel and to pull pieces across concepts. No existing community plugin I know of mixes across separate concept frames; I haven't searched the Figma community yet, which is step 0.

How it would work:

1. **A naming convention agents follow.** Each concept is a frame; pieces inside are named by role (`mix:header`, `mix:card`, `mix:controls`). Each concept's palette is a mode in one shared colour variable collection, and its fonts are text styles.
2. **Agents build concepts by script** with the Figma MCP (`use_figma`), using the builder-script approach already in `~/projects/ui-mixer/figma/`.
3. **The plugin panel** lists each slot (palette, heading font, body font, and each `mix:` piece) with chips for every concept. Picking a chip swaps that piece in a "Mix" frame (clone the node, or switch the variable mode). Undo, reset per slot, and **Copy settings** (JSON, same shape as the web mixer).
4. **Settings flow back to code**: the JSON is the spec the agent builds from.

Prototype scope (about half a day to a day of agent work): one screen, 4 concepts, three slots (palette, font pair, one layout piece), Copy settings. Development plugins load in the Figma desktop app from a manifest file, so Matt would install it once by hand.

Just for Matt at first, with real potential for the world (designers working with AI agents would want it).

Risks: the Figma connector in this session needs re-authorising before agents can build boards; the plugin can only swap pieces that agents named consistently, so the naming convention is the real product.

Freeze: this is a new project, so it waits for Matt's "build it".
