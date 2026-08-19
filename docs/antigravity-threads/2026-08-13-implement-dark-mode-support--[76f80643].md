---
title: "Implement Dark Mode Support"
date: "2026-08-13"
conversation_id: "76f80643-1954-47d9-8ec9-2da95b8052f8"
source: "antigravity"
---

# Implement Dark Mode Support

## User

Update CandidateList.tsx, MatchCard.tsx, and globals.css to ensure the "Not Right?" candidate picker responds dynamically to both Light and Dark modes:

1. Update `app/globals.css`:
Make sure CSS variables support both light and dark mode cleanly:
```css
:root {
  --bg-color: #08090a;
  --surface-bg: #121318;
  --card-border: rgba(255, 255, 255, 0.1);
  --text-primary: #ffffff;
  --text-secondary: #87888c;
  --input-bg: rgba(0, 0, 0, 0.4);
  --input-border: rgba(255, 255, 255, 0.15);
  --btn-secondary-bg: rgba(255, 255, 255, 0.08);
  --btn-secondary-border: rgba(255, 255, 255, 0.12);
  --card-item-bg: rgba(255, 255, 255, 0.04);
  --card-item-selected-bg: rgba(255, 255, 255, 0.12);
  --accent-color: #ffffff;
  --radius-lg: 8px;
  --radius-md: 6px;
}

@media (prefers-color-scheme: light) {
  :root {
    --bg-color: #ffffff;
    --surface-bg: #f4f4f6;
    --card-border: rgba(0, 0, 0, 0.1);
    --text-primary: #08090a;
    --text-secondary: #55555d;
    --input-bg: #ffffff;
    --input-border: rgba(0, 0, 0, 0.2);
    --btn-secondary-bg: rgba(0, 0, 0, 0.05);
    --btn-secondary-border: rgba(0, 0, 0, 0.12);
    --card-item-bg: #ffffff;
    --card-item-selected-bg: rgba(0, 0, 0, 0.08);
    --accent-color: #000000;
  }
}
```

2. Update `app/components/track-view/CandidateList.tsx`:
Replace hardcoded `#121318`, `#fff`, `rgba(0,0,0,0.4)` with the CSS variables defined above:
- Outer container: `background: 'var(--surface-bg)'`, `border: '1px solid var(--card-border)'`, `color: 'var(--text-primary)'`.
- Input field: `background: 'var(--input-bg)'`, `border: '1px solid var(--input-border)'`, `color: 'var(--text-primary)'`.
- Search button: `background: 'var(--btn-secondary-bg)'`, `border: '1px solid var(--btn-secondary-border)'`, `color: 'var(--text-primary)'`.
- Checkbox label: `color: 'var(--text-secondary)'`.
- Load More button: `background: 'var(--btn-secondary-bg)'`, `border: '1px solid var(--btn-secondary-border)'`, `color: 'var(--text-primary)'`.

3. Update `app/components/track-view/MatchCard.tsx`:
- Container:
  `background: isSelected ? 'var(--card-item-selected-bg)' : 'var(--card-item-bg)'`
  `border: isSelected ? '1px solid var(--accent-color)' : '1px solid var(--card-border)'`
- Title: `color: 'var(--text-primary)'`
- Subtitle: `color: 'var(--text-secondary)'`

Apply these edits carefully across `globals.css`, `CandidateList.tsx`, and `MatchCard.tsx`.

---

## Assistant

I have updated the requested files to support dynamic light and dark mode styling for the "Not Right?" candidate picker.

*   **[`globals.css`](file:///Users/matt/projects/music-cross-linker/app/globals.css)**: Added and organized comprehensive CSS variables for both themes.
*   **[`CandidateList.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/track-view/CandidateList.tsx)**: Applied the new CSS variables to the picker's components.
*   **[`MatchCard.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/track-view/MatchCard.tsx)**: Updated the card styling to use the new theme-responsive variables.

I have notified the parent agent of these changes.

---
