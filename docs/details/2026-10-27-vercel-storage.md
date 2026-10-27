# Vercel storage warning (2026-10-27)

## 10:45 What is using Vercel, and what to do

Matt got a Vercel usage warning and doesn't want to pay. Asked: find what's using it, cull junk, propose how to stay free.

---

### The real limit is uploads

- The only Blob store is `pages-tts` (project matt-pages): 23 MB, 444 files. Hobby allows 1 GB, so size is fine.
- The Hobby limit that bites is **Blob advanced operations: 2,000 per month** (every upload, copy or list counts). October so far: 445, and 408 of them happened today.
- Each new Readthrough recording costs 2 uploads (the mp3 and a JSON of word timings), in `api/tts-vercel.ts`. Since today every speed (75–200%) is its own recording, so listening at a new speed re-records every paragraph.
- On Hobby, going over does not bill you. Vercel **locks Blob for 30 days**, so every Readthrough voice would stop working until then.
- No Vercel email about it was found in Gmail (searched `from:vercel newer_than:3d`), so the warning was probably a dashboard banner.

---

### Everything else is far from its limit

October totals for the whole account: edge requests 166k of 1M, function calls 101k of 1M, data out 650 MB of 100 GB, builds normal. Old deployments (40 for matt-pages) don't count toward any Hobby storage limit.

---

### Why I deleted nothing

- Deleting blobs is free but saves nothing that matters (23 MB of 1 GB). Worse, it would force every deleted paragraph to be re-recorded, which costs more uploads, the exact thing that is running out.
- Deleting old deployments frees nothing on Hobby and could break older unlisted links.
- Rejected: `vercel blob list` to inspect files, because listing itself counts as an advanced operation.

---

### The fix I recommend

1. **Now, small:** save one file per recording instead of two (word timings inside the same file, or in the page's request), which halves uploads.
2. **Proper:** move the voice cache off Vercel Blob to Matt's VPS (his rule: prefer the VPS before a third-party host). Uploads there are unlimited. Cloudflare R2 is the fallback (1M uploads/month free, 10 GB).
3. **Guard:** a small daily check of `storage_blob` usage that warns at 1,500 uploads, so it never reaches the lock.

Handed to the Readthrough thread, since it owns `tts.ts` and the player, so two agents don't edit the same files.

### How to undo

Nothing was changed or deleted.

## 10:40 Uploads halved

The Readthrough thread shipped it: each recording is now one Blob upload (timings plus the mp3 in one JSON), and cache reads go straight to the public address with no head() or list() calls. I checked `api/tts-vercel.ts`: one `put()` per recording. Old two-file recordings still play; nothing was deleted. The VPS move still waits on Matt's 👍.
