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

## 12:15 Voice cache moved to the VPS

Matt gave 👍 to moving the Readthrough voice cache to his VPS.

---

### What runs on the VPS

- `tts-cache.service` (systemd, like photon-bridge): a tiny Bun server on 127.0.0.1:8796, files in `~/data/tts-cache/` (one JSON per recording, mp3 inside). Source is in the pages repo, `vps/tts-cache/`.
- Caddy routes `https://vps.mattmurphy.ca/tts/<key>.json` to it. Reads are public (same as Blob was). Saves need a secret token, generated fresh and stored only in `~/apps/tts-cache/.env` on the VPS and as `TTS_CACHE_TOKEN` in the matt-pages Vercel settings. Keys must be 20 hex characters; saves over 8 MB or with bad JSON are refused.
- The VPS disk has 14 GB free; a recording is about 25–400 KB, so tens of thousands of paragraphs fit.

---

### How Readthroughs use it

`api/tts-vercel.ts` now checks the VPS first, then Blob (for recordings made before today), and saves new recordings to the VPS only. If the VPS refuses or times out (8 s), it falls back to one Blob upload and logs it, so voices keep working if the VPS is down. Reads time out after 3 s.

---

### Tested live

- A fresh paragraph at 175% speed: recorded, saved on the VPS (new file appeared), and the second request was served from it.
- An older recording still plays from Blob, with nothing new written.
- Saving without the secret is refused (403).

---

### Left as is

- The 23 MB of old recordings stay in Blob so old Readthroughs keep their voices; reading them costs no uploads. Emptying the store later would make those paragraphs re-record once, onto the VPS.
- Not built: the daily usage warning. With uploads off Blob it should stay near zero.
- The deploy shipped the working tree, which included the Readthrough thread's uncommitted inline-code pause change in `tts.ts` (Matt asked for that change).

### How to undo this move

Revert the commit "Readthrough voice cache moves to the VPS" in the pages repo and run `pages deploy`; on the VPS, `sudo systemctl disable --now tts-cache` and restore `/etc/caddy/Caddyfile.bak-tts-cache`.
