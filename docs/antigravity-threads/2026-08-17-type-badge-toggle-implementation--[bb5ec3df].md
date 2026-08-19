---
title: "Type Badge Toggle Implementation"
date: "2026-08-17"
conversation_id: "bb5ec3df-da69-43cb-abd1-87e331fe70cc"
source: "antigravity"
---

# Type Badge Toggle Implementation

## User

Please make the following surgical improvements to `TypeBadge.tsx`, `globals.css`, and `urlResolver.ts`:

1. In `app/lib/urlResolver.ts`:
Fix `typeHint` override precedence in `resolveEntity`.
Ensure that if `typeHint` is `'album'` or `'track'`, it STRICTLY takes precedence over any database candidate checks or cached URL checks.
At line ~395 and ~415, only check `albumMatch` and `cached` when `!typeHint`.
And right before returning, ensure:
```ts
if (typeHint === 'album') isAlbum = true;
else if (typeHint === 'track') isAlbum = false;
```

2. In `app/components/track-view/TypeBadge.tsx`:
Implement an interactive, intuitive toggle with instant optimistic state and clear affordance:
- Provide an icon/switch indicator and clear hover/active states.
- Show current mode (`ALBUM LINK` or `TRACK LINK`) and a subtle toggle action (`Switch to Track` / `Switch to Album` or swap icon `⇄`).
- Use optimistic React state (`const [isPending, startTransition] = useTransition();` or `useState`) so clicking immediately flips the display while `router.push` runs.

3. In `app/globals.css`:
Add styles for `.type-badge-btn`, `.type-badge-label`, `.type-badge-switch-hint`, etc.:
- Styled pill with subtle border, nice transition on hover, clear cursor: pointer.
- On hover, reveal the switch hint (e.g. `opacity: 0.6` default or visible on hover, or an elegant interactive badge pill).

Ensure `bun run build` passes with zero errors.

---

## Assistant

The requested surgical improvements have been implemented and verified.

### Summary of Changes

1.  **`app/lib/urlResolver.ts`**:
    *   Updated `resolveEntity` to enforce `typeHint` precedence. Database candidate checks and cached URL checks are now skipped if `typeHint` is present.
    *   Explicitly forced `isAlbum` status based on `typeHint` before returning.
2.  **`app/components/track-view/TypeBadge.tsx`**:
    *   Implemented an interactive toggle using `React.useTransition` for optimistic UI updates.
    *   Added visual affordance with a "Switching..." state during navigation and a `⇄` icon hint.
3.  **`app/globals.css`**:
    *   Refined `.badge` styles to a modern pill-shaped design with hover transitions and pointer affordance.
    *   Added `.type-badge-switch-hint` styling for the interactive feedback element.

The project was validated by successfully running `bun run build`.

---
