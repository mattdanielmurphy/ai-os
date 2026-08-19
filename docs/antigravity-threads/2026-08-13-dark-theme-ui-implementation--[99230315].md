---
title: "Dark Theme UI Implementation"
date: "2026-08-13"
conversation_id: "99230315-90da-4321-aa65-38648830ced8"
source: "antigravity"
---

# Dark Theme UI Implementation

## User

Update CandidateList.tsx, MatchCard.tsx, and globals.css to fit the dark theme UI of music-cross-linker:

1. Update `app/components/track-view/CandidateList.tsx`:
- Use dark surface theme matching `--surface-bg` (`#121318`) / `rgba(255, 255, 255, 0.05)`, dark borders `rgba(255, 255, 255, 0.1)`, white text (`var(--text-primary)`), and muted text (`var(--text-secondary)`).
- Outer container: `background: '#121318'`, `border: '1px solid rgba(255, 255, 255, 0.1)'`, `color: 'var(--text-primary)'`, `borderRadius: '12px'`, `padding: '14px'`.
- "Not Right?" / "See search results" toggle button: subtle styling, `color: 'var(--text-secondary)'`, hover transition to white.
- Heading: "Select better match:" in clean white, `fontSize: '0.9em'`, `fontWeight: 600`.
- Input field: `background: 'rgba(0, 0, 0, 0.4)'`, `border: '1px solid rgba(255, 255, 255, 0.15)'`, `color: '#fff'`, `placeholderColor: '#888'`, `borderRadius: '6px'`, `outline: 'none'`.
- Search button: `background: 'rgba(255, 255, 255, 0.1)'`, `border: '1px solid rgba(255, 255, 255, 0.15)'`, `color: '#fff'`, `borderRadius: '6px'`, `cursor: 'pointer'`.
- Checkbox label: `color: 'var(--text-secondary)'`, `fontSize: '0.85em'`.
- "Load More Results" button: `background: 'rgba(255, 255, 255, 0.06)'`, `border: '1px solid rgba(255, 255, 255, 0.12)'`, `color: '#fff'`, `borderRadius: '6px'`, `padding: '10px'`, `fontWeight: 500`.

2. Update `app/components/track-view/MatchCard.tsx`:
- Card container style:
  `background: isSelected ? 'rgba(255, 255, 255, 0.12)' : 'rgba(255, 255, 255, 0.04)'`
  `border: isSelected ? '1px solid rgba(255, 255, 255, 0.3)' : '1px solid rgba(255, 255, 255, 0.08)'`
  `borderRadius: '8px'`
  `padding: '10px 12px'`
  `marginBottom: '8px'`
  `display: 'flex'`, `alignItems: 'center'`, `gap: '12px'`, `cursor: 'pointer'`
  `transition: 'all 0.15s ease'`
- Thumbnail: `width: '48px'`, `height: '48px'`, `objectFit: 'cover'`, `borderRadius: '6px'`.
- Text color: Title in `var(--text-primary)` / `#ffffff` with `fontWeight: 500`, Subtitle/artist in `var(--text-secondary)` / `#87888c` with `fontSize: '0.85em'`.
- Selected icon: `<IconCheck size={18} color="#1db954" />` (or accent checkmark).

Inspect both files and apply these styled updates cleanly.

---

## Assistant

The dark theme UI updates have been applied to `CandidateList.tsx` and `MatchCard.tsx`.

### Changes Applied:
- **`CandidateList.tsx`**:
    - Set container to `background: '#121318'`, `border: '1px solid rgba(255, 255, 255, 0.1)'`, and added `borderRadius: '12px'`.
    - Styled input field, search button, "Load More Results" button, and text colors to match the dark theme.
    - Updated toggle button ("Not Right?" / "See search results") with subtle styling and hover transition.
- **`MatchCard.tsx`**:
    - Updated card container styling with dynamic background/border based on selection status, `borderRadius: '8px'`, and flex layout.
    - Adjusted thumbnail size and styling.
    - Set text colors to use `var(--text-primary)` and `var(--text-secondary)`.
    - Updated selected icon to `<IconCheck size={18} color="#1db954" />`.

---
