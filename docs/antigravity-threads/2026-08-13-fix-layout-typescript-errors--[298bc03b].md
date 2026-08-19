---
title: "Fix Layout TypeScript Errors"
date: "2026-08-13"
conversation_id: "298bc03b-283b-499f-a234-64a5f868cc05"
source: "antigravity"
---

# Fix Layout TypeScript Errors

## User

Fix TypeScript error in `app/layout.tsx`:
Add back `import type { Metadata } from 'next';` at line 1.

Check `app/layout.tsx` and make sure it reads:
```tsx
import type { Metadata } from 'next';
import UrlTipFooter from './components/UrlTipFooter';
import './globals.css';

export const metadata: Metadata = {
  title: 'Music Cross Linker - Universal Track Links',
  description: 'Search and cross-link tracks across YouTube, Spotify, and Apple Music.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
        <UrlTipFooter />
      </body>
    </html>
  );
}
```

Fix `app/layout.tsx` now.

---

## Assistant

The `app/layout.tsx` file has been updated to include the missing `Metadata` import.

---
