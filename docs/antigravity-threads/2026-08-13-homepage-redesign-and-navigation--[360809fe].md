---
title: "Homepage Redesign And Navigation"
date: "2026-08-13"
conversation_id: "360809fe-8f65-4571-bc6f-a813b1e1a2f9"
source: "antigravity"
---

# Homepage Redesign And Navigation

## User

Please update `app/page.tsx` and `app/globals.css` (if needed) for the homepage redesign.

Requirements:
1. Allow the user to either paste a URL OR type artist and album/track.
2. If artist and album/track fields are filled, submitting the form navigates to `/<artist>/<albumOrTrack>` (e.g. `router.push('/' + encodeURIComponent(artist.trim()) + '/' + encodeURIComponent(albumOrTrack.trim()))`).
3. If URL/search input is filled, submitting navigates to `/<trimmedValue>`.
4. Provide a tab/toggle or clear visual layout so the user can easily switch between pasting a URL / searching, or entering Artist + Album/Track directly, OR single form with both options clearly presented.
5. Add a helpful note/tip explaining that users can also append/paste full media links from YouTube, Spotify, or Apple Music directly into the browser URL bar (e.g. `music.example.com/https://open.spotify.com/...`).

Here is `app/page.tsx` context:
```tsx
"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

export default function Home() {
  const router = useRouter();
  const [mode, setMode] = useState<"search" | "fields">("search");
  const [urlOrSearch, setUrlOrSearch] = useState("");
  const [artist, setArtist] = useState("");
  const [albumOrTrack, setAlbumOrTrack] = useState("");

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (mode === "fields") {
      if (artist.trim() && albumOrTrack.trim()) {
        router.push("/" + encodeURIComponent(artist.trim()) + "/" + encodeURIComponent(albumOrTrack.trim()));
      }
    } else {
      const trimmed = urlOrSearch.trim();
      if (trimmed) {
        // If it starts with http(s)://, strip protocol or pass as is based on existing behavior:
        // note: app handles router.push("/" + encodeURIComponent(trimmed)) or raw path.
        router.push("/" + encodeURIComponent(trimmed));
      }
    }
  };

  ...
```

Make sure:
- Toggle tabs or segmented control to switch between "Paste Link / Search" and "Artist & Track/Album".
- Alternatively, auto-detect or dual form, but tabbed or clear input modes look cleanest.
- Display a sleek tip note card at the bottom:
"💡 Tip: You can also append any YouTube, Spotify, or Apple Music link directly to our URL in your browser address bar!"
- Update CSS in `app/globals.css` if necessary for tabs, note cards, input rows, etc.

Edit `app/page.tsx` and `app/globals.css` now.

---

## Assistant

The homepage redesign has been completed. `app/page.tsx` now includes a tabbed interface for switching between URL/search input and manual artist/track entry, along with a helpful tip card. Corresponding CSS styles have been added to `app/globals.css`.

A notification has been sent to the parent agent.

---
