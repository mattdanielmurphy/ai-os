---
title: "Refactor CandidateList Component Styling"
date: "2026-08-13"
conversation_id: "fa11adbd-497c-4752-a1c8-b9013badb2a3"
source: "antigravity"
---

# Refactor CandidateList Component Styling

## User

Update CandidateList.tsx:
Remove the card background/border/padding wrapper from the outer `<div style={{ marginTop: '10px' }}>` so that the "Not Right?" / "Close" text button remains a plain link as it originally was, without an extra card box surrounding it when closed.

Specifically:
- Outer div: `<div style={{ marginTop: '10px' }}>` (no background, border, or padding).
- Inner div when `isOpen` is true: `<div style={{ marginTop: '10px', background: 'var(--surface-bg)', border: '1px solid var(--card-border)', borderRadius: 'var(--radius-lg)', padding: '14px', color: 'var(--text-primary)' }}>`.

Apply this change to `CandidateList.tsx`.

---

## Assistant

The changes to `CandidateList.tsx` have been successfully applied. The outer container for the "Not Right?" / "Close" button no longer has card styling, ensuring it remains a plain link until expanded. The styling has been moved to the inner div that wraps the expanded content.

You can verify the changes in [`CandidateList.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/track-view/CandidateList.tsx).

---
