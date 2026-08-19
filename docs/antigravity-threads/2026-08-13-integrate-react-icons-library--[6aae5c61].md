---
title: "Integrate React Icons Library"
date: "2026-08-13"
conversation_id: "6aae5c61-92b0-4634-ad8f-1573792db7d7"
source: "antigravity"
---

# Integrate React Icons Library

## User

We installed `react-icons`. Please update `app/components/track-view/PlatformButton.tsx` and `app/components/track-view/LoadingChip.tsx` to use the official solid Simple Icons brand logos from `react-icons/si` (`SiSpotify`, `SiApplemusic` or `SiApple`).

Let's check imports:
Import `SiSpotify` and `SiApplemusic` (or `SiApple`) from `'react-icons/si'`.

In `PlatformButton.tsx`:
Remove the custom inline `SolidSpotifyIcon` and `SolidAppleIcon` SVGs.
Set up ICONS map:
```tsx
import { SiSpotify, SiApple } from 'react-icons/si';

const ICONS: Record<string, any> = {
  spotify: SiSpotify,
  apple_music: SiApple,
};
```
And render: `<Icon size={28} style={{ flexShrink: 0 }} />`

In `LoadingChip.tsx`:
Same thing - import `SiSpotify` and `SiApple` from `'react-icons/si'`.
Replace custom icon definitions with `SiSpotify` and `SiApple`.

Please update both files cleanly.

---

## Assistant

The requested updates to `app/components/track-view/PlatformButton.tsx` and `app/components/track-view/LoadingChip.tsx` have been completed. Both files now import `SiSpotify` and `SiApple` from `react-icons/si` and have replaced the custom inline SVG icons with these official brand logos.

---
