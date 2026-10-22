# 2FA code "G-" prefix fix

## 11:15 Strip "G-" from auto-copied 2FA codes

Asked: the 2FA auto-copy utility keeps Google's "G-" prefix (e.g. `G-000164`), which Google's field rejects. Recreate an improved version in mac-utilities if needed.

---

### What the utility is

[MessAuto](https://github.com/LeeeSe/MessAuto) 1.3.0 (open-source Rust app, `/Applications/MessAuto.app`, started by `~/Library/LaunchAgents/Messauto.plist`). It watches Messages and Mail, finds a keyword ("code", "verification"…), then picks the regex match closest to it. Its log (`~/Library/Application Support/messauto/logs/app.log`) shows `Found verification code in message: G-000164` at 10:58 today.

---

### Why no rebuild

The regex lives in `~/Library/Application Support/messauto/config.toml` (`verification_regex`) and is re-read on every message (`Config::load()` inside `extract_verification_code`), so a config edit is the whole fix and needs no restart. Upstream deliberately keeps `G-` (its own test expects `G-23414`), so the default will never change. A mac-utilities rebuild was rejected: same behaviour for far more code.

---

### The new regex

```
(?<=\b[A-Z]-)[0-9]{4,8}\b|(?![A-Z]-[0-9]{4,8}\b)(?<!\b[A-Z]-)(?<!\b[A-Z])(?=[a-zA-Z0-9-]*[0-9])[a-zA-Z0-9-]{4,8}
```

- Alt 1: digits right after a single capital letter + dash at a word start (`G-000164` → `000164`).
- Alt 2: the original pattern, blocked from starting at `G` or `-` of such a prefix.
- Codes like `RKJ-YP6` (multi-letter prefix, letters after the dash) are kept whole.

---

### Testing

Harness in the session scratchpad: upstream `parser.rs` logic + fancy-regex 0.16.1 + toml 0.8 (same crates as MessAuto), reading the live config file. All 24 upstream test cases pass except the one that expects `G-23414` (now `23414`, intended). Added cases: `G-000164 is your Google verification code.`, `Your Google verification code is G-123456` → digits only. Old regex failed all three.

Untested: a real incoming Google text (next one will confirm).

---

### Undo

`cp "~/Library/Application Support/messauto/config.toml.bak-2026-10-22" "~/Library/Application Support/messauto/config.toml"`

## 11:35 Own Hammerspoon 2FA utility (replacing MessAuto)

Asked: replace MessAuto entirely with a lightweight Hammerspoon utility in the suite (trust + matching UI).

---

### Built otp_copy module

`~/.hammerspoon/modules/otp_copy.lua`, menu "2FA Code Auto-Copy (Messages & Mail)", in `suite.SHAREABLE`, documented in UTILITIES.md, published to mac-utilities (d6f3e59).
- Messages: pathwatcher on ~/Library/Messages; on chat.db change, async `/usr/bin/sqlite3 -readonly -json` for new incoming rows (last 10 min). Decodes `attributedBody` when `text` is empty (newer macOS).
- Mail: pathwatcher on ~/Library/Mail for new `.emlx`; Lua MIME parser (multipart, quoted-printable, base64, encoded subjects), prefers text/plain.
- Extraction rewritten in Lua (MessAuto's regex approach replaced): needs a keyword; nearest candidate within 100 bytes; digits preferred; `G-123456` → `123456`; rejects URL/ID tokens and mixed-case strings (fixes MessAuto's `01Wt4afu` / `Nova-3` false positives in your log).
- Rejected: hs.sqlite3 (sync on main thread, blocks key taps); one-letter-prefix rule kept narrow (only single capital + dash + digits) so codes like `RKJ-YP6` stay whole.

---

### Safer clipboard handling

Copied with `org.nspasteboard.ConcealedType` + `TransientType`, so Pastebot/Maccy/Raycast skip it. Wiped after 2 min, restoring what was on the clipboard before (unless you copied something since). Back-to-back codes keep the original pre-code clipboard. Writes go through `claudeControl.withInput`.

---

### Code pill

Green tinted pill (claude_notify "done" palette), new `otp_code` HUD slot bottom-left above the reload ↻ (layout test passes). Fades after 12 s, click dismisses. Bumped to 96% opacity after the first screenshot showed text bleeding through. Not draggable: it's a transient toast, not a HUD.

---

### Full Disk Access needed

Hammerspoon can't read chat.db or Mail without Full Disk Access (checked: both unreadable). Granting it is a security setting, so only Matt can do it. Until then the module alerts once and idles, so MessAuto stays on until the new one is confirmed working.

---

### Tests and what's untested

`lua tests/otp_copy_test.lua`: all MessAuto upstream cases + Google + your log's false positives + attributedBody + emlx parsing pass. Live: clipboard types and pill verified on screen. Untested: real Messages/Mail watchers (blocked on Full Disk Access), and the attributedBody layout on your actual chat.db.

---

### Undo

Toggle it off in the ⚙︎ menu, or `git revert 6c4d403` in ~/.hammerspoon. MessAuto is untouched (still running).

## 11:45 Full Disk Access granted, MessAuto switched off

---

### Real messages verified

With Full Disk Access, ran the module's decoder + extractor over your last 300 incoming texts: 268 had text only in attributedBody, all 268 decoded. Codes found: Google 000164 plus the same codes MessAuto logged (394890, 367502, 757847), bank/CIBC/TD/TELUS one-time codes, and one "buzz code 7613" (a door code; harmless). None of MessAuto's junk matches (01Wt4afu etc.). Message contents were read only to check this, not saved.

---

### MessAuto switched off

`launchctl bootout` + quit, plist moved to ~/Library/LaunchAgents/Archive/Messauto.plist, its own launch_at_login set false. App still in /Applications (move to Trash if you like). Undo: move the plist back and `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/Messauto.plist`.

Still untested: the Mail path on a real incoming email (parser tested on synthetic mail).
