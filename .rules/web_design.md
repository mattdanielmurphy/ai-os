# Web Design & Anti-Slop Policy

## Mandatory Proactive Generator Rule
- **Default Behavior:** Whenever starting a new web project, creating an HTML artifact, or implementing a new UI surface, agents MUST run `python3 /Users/matt/projects/ai-os/scripts/generate_design_brief.py` FIRST to receive a randomized, visually harmonized design brief.
- **Exception:** Only skip running the design brief generator if the user explicitly specifies a specific brand palette or visual style (e.g. "make it look like Stripe" or "use parchment theme").

## Permanently Banned Aesthetics ("AI Slop")
1. **Aggressive Tech Gradients:** Banned. Do NOT use purple-to-pink, blue-to-violet, or neon gloss gradients on text, buttons, hero elements, or card borders.
2. **Generic Tech Hues:** Avoid default unthinking indigo/violet/purple accents unless explicitly specified by a brand design system.
3. **Slop Decoration:** No unearned glassmorphism/backdrop blurs without real surface depth, no accent left-rail strips on cards, no icon toppers centered over every heading, and no monument stat numbers taking up storytelling space.
4. **Compositional Defaulting:** Never default to centered hero + 3 identical card tiles. Commit to a surface archetype before writing layout or tokens.

## Preferred Design Systems & Workflow
1. **Claude Design Doctrine (`claude-design`):**
   - Focus on surface archetype commitment first (Monitor, Operate, Compare, Configure, Decide/Learn, Explore, Command/Inspect).
   - Use warm paper/parchment surfaces (`#f5f4ed`), editorial serif typography (Georgia / Anthropic Serif for headlines), terracotta (`#c96442`) accents, or crisp monochromatic surfaces instead of cold AI gradients.
2. **Linear Precision (`popular-web-designs` / `linear.app.md`):**
   - For dark UI surfaces, use deep near-black backgrounds (`#08090a`), translucent white borders (`rgba(255,255,255,0.05)` to `0.08`), Inter with tight display tracking (`-1px` to `-1.5px`), and single subtle indigo/violet accents used sparingly.
3. **Execution:**
   - Execute the 10-point Slop Diagnostic before finalizing web interfaces to score and eliminate AI slop tells.
