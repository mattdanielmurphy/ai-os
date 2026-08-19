---
title: "Platform Button Style Updates"
date: "2026-08-13"
conversation_id: "a15491a9-dff5-4358-91dc-607e317a9a84"
source: "antigravity"
---

# Platform Button Style Updates

## User

Please update app/components/track-view/PlatformButton.tsx, app/components/track-view/LoadingChip.tsx, and app/globals.css to address user requests:

1. **Button sizing & alignment**:
   - `btn-link` elements in `app/globals.css` (and inside `PlatformButton.tsx` / `LoadingChip.tsx`) must maintain the exact same height and width across platform buttons regardless of text content length.
   - Text layout should be left-aligned consistently in both buttons (currently `.btn-link` has `justify-content: center` in `globals.css` while inline style had `justify-content: flex-start` or text-align left, but we should make `.btn-link` left-aligned by default with `justify-content: flex-start`).
   - Sizing: Give `btn-link` fixed height (or min-height / flex dimensions), exact width or `width: 100%` inside grid columns, padding, and text containment.
   - Shrink text slightly so it fits (e.g. title font-size around `0.9rem` / `14px` or `0.85rem`, artist font-size around `0.8rem` / `13px`), and add clean text truncation (`white-space: nowrap; overflow: hidden; text-overflow: ellipsis;`).

2. **Solid Icons**:
   - Instead of outline icons like `@tabler/icons-react`'s `IconBrandSpotify` / `IconBrandApple`, replace them with solid SVG icons (or solid Tabler variants if available, or inline clean solid SVGs).
   - Let's provide solid filled SVGs for Spotify and Apple (Apple logo is naturally solid filled path; Spotify logo should be solid filled green/white circle icon with cutouts or filled circle).
   - For example:
     - Apple solid SVG: standard Apple logo silhouette filled.
     - Spotify solid SVG: solid circle background with cut-out sound waves, or solid official Spotify badge style.
     - Or custom React SVG components `SolidSpotifyIcon` and `SolidAppleIcon`.

Let's check the exact details:
In `PlatformButton.tsx`:
Replace `IconBrandSpotify` and `IconBrandApple` with solid inline SVG components (or dedicated SVG icons).
Make title and artist containers truncate cleanly:
```tsx
<div style={{ flex: 1, minWidth: 0, textAlign: 'left' }}>
  <div style={{ fontWeight: 'bold', fontSize: '0.875rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{cleanTitle(active.title)}</div>
  <div style={{ fontWeight: 'normal', fontSize: '0.8rem', opacity: 0.8, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{active.artist}</div>
</div>
```

In `LoadingChip.tsx`:
Ensure icon is consistent with solid icons, layout matches `.btn-link`.

In `globals.css`:
Update `.btn-link`:
```css
.btn-link {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 0.75rem;
  padding: 0.6rem 0.9rem;
  height: 64px;
  width: 100%;
  border-radius: var(--radius-md);
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
  color: #fff;
  border: 2px solid rgba(255, 255, 255, 0.1);
  box-sizing: border-box;
}
```

Please perform these edits to `app/components/track-view/PlatformButton.tsx`, `app/components/track-view/LoadingChip.tsx`, and `app/globals.css`.

---
