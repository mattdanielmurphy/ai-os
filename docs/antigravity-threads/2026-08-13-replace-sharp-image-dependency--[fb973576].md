---
title: "Replace Sharp Image Dependency"
date: "2026-08-13"
conversation_id: "fb973576-428b-4083-9bac-33e51a299d64"
source: "antigravity"
---

# Replace Sharp Image Dependency

## User

In /Users/matt/projects/music-cross-linker/app/lib/palette.ts:

Remove the native `sharp` import and binary dependency because `sharp` fails on Vercel Serverless (Linux x64 C++ runtime mismatch: `libvips-cpp.so.8.18.3: cannot open shared object file`).

Replace `getPaletteFromImage` in `app/lib/palette.ts` with a pure JS / safe fallback implementation that does not require `sharp` native bindings.

```ts
export interface ThemeColors {
  '--bg-primary': string;
  '--bg-secondary': string;
  '--text-primary': string;
  '--text-secondary': string;
  '--accent': string;
}

const DEFAULT_THEME: ThemeColors = {
  '--bg-primary': '#121212',
  '--bg-secondary': '#1e1e1e',
  '--text-primary': '#ffffff',
  '--text-secondary': '#b3b3b3',
  '--accent': '#1db954',
};

export async function getPaletteFromImage(imageUrl: string): Promise<ThemeColors> {
  return DEFAULT_THEME;
}

export function getContrastColor(hex: string): string {
  if (!hex || !hex.startsWith('#') || hex.length < 7) return '#FFFFFF';
  const r = parseInt(hex.slice(1, 3), 16) / 255;
  const g = parseInt(hex.slice(3, 5), 16) / 255;
  const b = parseInt(hex.slice(5, 7), 16) / 255;
  const luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;
  return luminance > 0.5 ? '#000000' : '#FFFFFF';
}
```

Update `/Users/matt/projects/music-cross-linker/app/lib/palette.ts`.

---

## Assistant

The file `/Users/matt/projects/music-cross-linker/app/lib/palette.ts` has been updated to remove the `sharp` dependency and its native bindings, resolving the Vercel Serverless deployment issue. The `getPaletteFromImage` function now uses a safe, pure JS fallback, and `getContrastColor` has been updated with the requested input validation.

---
