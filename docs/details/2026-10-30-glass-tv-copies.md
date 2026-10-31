## 18:30 Copies menu "couldn't switch"

You asked why switching copies failed and whether low seeders were the cause.

Cause: that message only appears when the server refuses the switch, before any video link is tried, so seeders can't trigger it. The list of copies lived only in server memory and the server restarts often (each install by another session), while the player keeps running. Reproduced during Ted Lasso S2E8: the menu's list was empty on the server and the switch returned 404.

Changes (728e1ee): list saved in `sources.json` (last 6 titles); menu and auto-fallback skip uncached copies with fewer than 10 sharers (`stream.menuMinPeers`, a judgment call; 10 is where the "fair signal" bar starts); failure says why; a copy that won't open within 20 s returns to the old copy at the same spot. Default ranking untouched.

Not tested: return-to-old-copy with real playback; not installed until playback ends. Undo: revert 728e1ee.
