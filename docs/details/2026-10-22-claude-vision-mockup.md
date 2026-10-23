# Claude Vision: UI mockup (2026-10-22)

## 18:10 First Figma mockup

Matt asked (via coordinator): continue the Claude vision idea, give him a UI mockup in Figma, and have Claude take the first design pass itself (no blind attempt from him tonight). The "blind two drafts" idea moved to its own thread.

Figma file: https://www.figma.com/design/i9plYkcQ8nqn6xiwk24CoZ (his drafts, "Claude Vision HUD mockup").

---

### Main view layout

One 1440x900 desktop window:
- **Viewer** (big, left): the frame Claude is reading, with its markup drawn on top. Orange solid box = where focus is now, blue dashed box = where it was, dotted arrow = motion, numbered labels say what each mark means. Toggles top-right: Markup, Motion, Diff heatmap. Frame number + timestamp bottom-right.
- **Timeline** (bottom): filmstrip of frames. Frames Claude actually opened get an orange border; others are dimmed. Under each, a "change" bar (blue when the frame differs a lot from the previous one), so you can see where motion happened and whether Claude looked there.
- **What Claude sees** (right): one note per frame Claude opened, in plain words. Active note highlighted. A "Motion" box summarises movement, and says honestly it's read from frame diffs, not live video. "Ask about frame 42…" box at the bottom.
- **Top bar**: source recording, a live "Claude is looking at frame 42" pill, and a UI / Sports mode switch (Sports is the sports-analytics use case he floated; not designed yet).

---

### Compact floating pill

A small pill (below the main frame) for when Claude is working in the background: thumbnail + "Looking at frame 42 of 180" + one line of what it noticed. Click would open the full view. It would take a HUD slot from `hud_slots.json` if built.

---

### Decisions and why

- Content is the PS5 home menu because that's the real recorder he has; tiles are grey blocks, not real art.
- Orange = Claude's attention, blue = change/motion. These are placeholder colours: the master palette isn't picked yet, so this mockup's colours must not be treated as final (rule: never invent a colour). No terracotta.
- Light mode only for now. Dark mode not drawn yet.
- Built from editable Figma layers; the frame thumbnail is a component.
- Rejected: video-scrubber-first layout (Claude only sees stills, so stills-first is more honest); a chat-first layout (the point is seeing what Claude sees).

### Not done / risks

- Sports mode, dark mode, empty states not drawn.
- Nothing built; mockup only. Build waits for his 👍.
- Undo: delete the Figma file from his drafts.
