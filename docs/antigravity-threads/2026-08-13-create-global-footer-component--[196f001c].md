---
title: "Create Global Footer Component"
date: "2026-08-13"
conversation_id: "196f001c-5be7-4862-a355-4a593383102a"
source: "antigravity"
---

# Create Global Footer Component

## User

Please create a reusable footer component `app/components/UrlTipFooter.tsx` and integrate it into `app/layout.tsx` so the note about pasting YouTube, Spotify, or Apple Music URLs is displayed globally on all pages.

1. Create `app/components/UrlTipFooter.tsx`:
```tsx
import React from "react";

export default function UrlTipFooter() {
  return (
    <footer className="global-url-tip-footer">
      <p className="url-tip-text">
        💡 <strong>Tip:</strong> Did you know? You can append any full YouTube, Spotify, or Apple Music URL directly after our domain in your browser bar! (e.g. <code>/https://open.spotify.com/...</code>)
      </p>
    </footer>
  );
}
```

2. Update `app/layout.tsx` to include `<UrlTipFooter />` at the bottom of `<body>`.

3. Update `app/globals.css` to add styles for `.global-url-tip-footer`:
```css
.global-url-tip-footer {
  text-align: center;
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.03);
  border-top: 1px solid var(--card-border, rgba(255, 255, 255, 0.08));
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: auto;
}

.global-url-tip-footer code {
  background: rgba(255, 255, 255, 0.08);
  padding: 0.15rem 0.35rem;
  border-radius: 4px;
  font-family: monospace;
  color: var(--text-primary);
}
```

4. In `app/page.tsx`, if there is a redundant local tip card, remove or refine it so it doesn't clash with the global footer.

Do this now using direct file creation/editing tools.

---
