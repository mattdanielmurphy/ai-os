# AutoStream speed-up (2026-10-26)

## 13:40 Stream load time cut to the Comet floor

Matt asked: AutoStream (Stremio addon, VPS `oracle-vps`, `~/AutoStream`, systemd `autostream`, port 7010) takes ~7s to show streams; optimize it.

---

### Where the 7 seconds went

From the journal for a 7.9s request (tt26657236):
- 5.0s: "Validating IMDB ID" — a blocking Cinemeta call in `utils/id-correction.js`. It fetches `/meta/series/<id>.json`, which now 307-redirects to cinemeta-live; Node's `https.get` doesn't follow redirects, so it fails after 0.4–5s and returns nothing. The correction table it guards is empty.
- ~2s: Comet (ElfHosted, the only active source) + metadata, in parallel.
- 0.3–1s: RealDebrid key check, run after the sources finished, and never cached (lookup key `realdebrid:<key>` vs stored `rd:<key>`).

---

### What changed (commit 6b3a4a2, pushed to mattdanielmurphy/AutoStream master)

1. ID check is now synchronous (known corrections still apply). Metadata still comes from `fetchMeta`, in parallel with Comet.
2. RD key validation starts alongside the source fetches.
3. Cache lookup uses the short name, so repeat requests skip the RD API call.
4. Validation cache cleanup age 10 → 30 min (matches the 30-min trust window).

---

### Results

Cold requests (fresh restart, same 4 titles): before 1.1–3.0s (and up to ~8s when Cinemeta was slow), after 1.1–2.0s. Overhead outside Comet: was 0.4–6s, now ~70ms. Repeat requests: 8–30ms (unchanged, in-memory cache).

---

### What's left: Comet itself

Comet takes 0.5–1.5s per title upstream. Tested limiting `maxResultsPerResolution` to 10: no speed gain, so left as is. Further options: self-host Comet on the VPS, or prefetch the next episode in the background so autoplay is instant.

---

### Untested / risks

- Not tested from the Stremio app itself, only with curl against the addon on the VPS.
- Undo: `ssh oracle-vps 'cd ~/AutoStream && git revert 6b3a4a2 && sudo systemctl restart autostream'`. Pre-change copy also at `~/AutoStream/tmp/server.js.bak`.
- Noticed: the journal logs the full RD API key in the "Configuration path" line. Worth masking.
