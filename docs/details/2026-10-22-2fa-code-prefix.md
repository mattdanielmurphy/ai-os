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
