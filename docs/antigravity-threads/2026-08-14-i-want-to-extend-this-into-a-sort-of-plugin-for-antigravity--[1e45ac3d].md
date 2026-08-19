---
title: "I want to extend this into a sort of plugin for Antigravity. I'd like to add a..."
date: "2026-08-14"
conversation_id: "1e45ac3d-73c6-4c2d-8d28-e40982df1125"
source: "antigravity"
---

# I want to extend this into a sort of plugin for Antigravity. I'd like to add a...

## User

I want to extend this into a sort of plugin for Antigravity. I'd like to add a few of the things below.
```
What comes to mind initially:
- A way to see the current context of the thread
- “Open project in Zed” button
- a way to see what mcp sub agents are working on inline
- a way to select settings like
- delegation: ruthless (“strict”) / heavy / light
- sub agent models
- quota info & button to switch to alt account

How to do Open project in Zed button (and other actions): not sure exactly.
In fact, this is an interesting project because there’s so many bizarre limitations to this, that we have to constantly think of workarounds. But that’s what makes it fun when we can get really nice results.
Honestly I would bet that we could get a lot of functionality out of this yet.
I can’t exactly remember the link situation.
I mean, I know that you can have links that open in the browser.
But I initially was working on a way to try and click a a link to hit a server endpoint, and I could do that, but it would always actually open that url in Chrome.

So unless we’re going to open something in chrome, and I guess it wouldn’t be the *worst thing* honestly; it’d let us make a really legit UI if we wanted to do something complex…

Now the drawback to file URLs is they tend to open in a new tab as an artifact.
I haven’t tried something that Antigravity wouldn’t be likely to try and open, even an executable…
But honestly I bet they’d consider that a security bug and patch it (an executable especially). But, if it could do *something* with a link click, that gives us a lot. Something meaning it triggers an effect that can be reliably observed by our backend server which could manipulate the main md artifact in some way.
But honestly, i think we still could do a surprising amount with a generated md with html and css.

I’m now curious if we can make a tabbed interface somehow.
I mean, without a way to click back to the backend, and I don’t have one yet… honestly I can’t quite say. I know you can do a lot with restyling checkboxes, so I could theoretically have state… the thing is, we only have inline css. And also I’m not sure how it’d work to pass down styles from a span wrapping a checkbox.
Yeah I’m almost positive to use a checkbox trick you need to use like a pseudo selector or something. Like ::after or ::checked or something.
```

Now, you are NOT going to be able to add all these features because you don't have the FULL project context.
BUT, you can help us try to solve the biggest dilemma: interactivity.
Basically a way to click and have that trigger something in our backend which then updates the markdown file.

---

## Assistant

## Perplexity — 06:50 PM

The core insight: exploit URL-scheme dispatch, not `file://`

You've already found the two failure modes: `http(s)://` links get hijacked by the OS's registered default-browser handler (Chrome), and `file://` links get intercepted by Antigravity's own artifact-preview logic (opens a new tab). Both of those are claimed protocols. The fix is to use an **unclaimed custom URI scheme** that *you* register a handler for.

This isn't speculative — Antigravity itself ships as a registered scheme handler. Its installer registers `antigravity-ide://` as a deep-link handler so external tools can jump back into the IDE. Security researchers have flagged exactly this class of editor (VS Code, Cursor, Antigravity) for spawning a process or invoking handler logic the moment a link with a registered custom scheme is clicked in a preview/webview. That's the mechanism working in your favor: when the Antigravity markdown renderer hits a link whose scheme isn't `http(s)` or `file`, it doesn't silently swallow it or force it into Chrome — it hands it to the OS's `LSCopyDefaultHandlerForURLScheme` / `xdg-open` resolution, same as it does for its own scheme. There's even an open complaint that Antigravity *doesn't* handle `vscode://file` links, with the maintainers suggesting the fix is "register a custom protocol" — confirming custom-scheme registration is the sanctioned, supported path here, not a hack that'll get patched like an executable-launch trick would.
gist.github
+2

Concrete architecture

**1. Register your own scheme, e.g. `agyclick://`.** On macOS this is a tiny app bundle — no GUI needed, just an `Info.plist` with a `CFBundleURLTypes` entry pointing at a stub binary (Platypus or a two-line Swift/AppleScript wrapper works fine). Register it once with `lsregister`.


```
xml
<!-- Info.plist -->
<key>CFBundleURLTypes</key>
<array><dict>
  <key>CFBundleURLName</key><string>com.you.agyclick</string>
  <key>CFBundleURLSchemes</key><array><string>agyclick</string></array>
</dict></array>
```


The stub does one thing: grab the incoming URL (`agyclick://swap_turn?conv=abc123&turn=3`), curl it to a `localhost`-only server you run, and exit.

**2. Run a tiny local HTTP listener** (you already have the pattern — `swap_turn.py` in your repo is literally an HTTP handler). It decodes the query params, performs the backend mutation (swap a turn, change delegation mode, whatever), and then calls `gen_conversation_md.generate()` directly (in-process, like `watch_transcripts.py` already does).

**3. Let the existing watcher close the loop.** Since `watch_transcripts.py` re-renders on file mtime/size change, your handler doesn't need to push anything to the UI — it just needs to win the race before the next poll tick. Antigravity re-reads the artifact file itself.

**4. Embed the click** as a plain markdown link with your scheme:


```
text
[⚙️ Switch to strict delegation](agyclick://set_delegation?mode=strict&conv=abc123)
```


No `<script>`, no JS execution required — this is just link-scheme dispatch, which is a much more durable trick than trying to smuggle an executable (which, as you guessed, would get flagged and patched fast).

What this buys you for your specific features

**Delegation / sub-agent model / account-switch settings**: each becomes a link (or small link-menu) hitting `agyclick://set_setting?...`, backend rewrites a config file the agent reads, artifact re-renders to reflect new state.

**"Open in Zed" button**: same mechanism, but the handler's payload is a `zed://file/<path>` or shell `open -a Zed <path>` call — you're routing through *your* handler first so you control the launch, rather than depending on Antigravity to natively understand a `zed://` link.

**Sub-agent inline status**: you already built `get_subagent_progress()` — no click needed there, just poll and re-render.

On the checkbox/CSS-tabs idea — why it's a dead end here

The `:checked ~ .sibling` trick requires a real stylesheet (`<style>` block or `<link>`), because inline `style=""` attributes can't express sibling-combinator or pseudo-class rules — you can't put `:checked` logic *inside* the checkbox's own inline style. Your `gen_conversation_md.py` already only ever emits inline styles on `<span>`s, which strongly suggests `<style>`/`<script>` tags get sanitized out of the artifact renderer (standard markdown-preview hardening). So CSS-only tabbed state is very likely unreachable without a stylesheet channel.

Given the URL-scheme approach above, you don't need it anyway: implement tabs **server-side**. A tab-link click (`agyclick://set_tab?panel=logs`) hits your backend, which rewrites the generated markdown so only the selected section's body is expanded (collapse the rest into `<details>` or omit them). The "tab state" lives in your Python generator, not in CSS — which is more robust and lets you do far more than a checkbox hack ever could (e.g. tabs whose content depends on live subagent state).

**One caution**: OS URL-scheme registration is somewhat sticky/cached (you may need `lsregister -f` or a logout to pick up changes during development), and you should put a shared secret in the query string or bind your listener to `127.0.0.1` only, since any process on the machine can invoke a registered URL scheme.

---

## User

yeah... sadly URl-scheme doesn't work.
```

<div style="background: #1e1e2e; border: 2px solid #89b4fa; padding: 16px; border-radius: 12px; margin-bottom: 20px; text-align: center; color: #cdd6f4; font-family: sans-serif;">
<h3 style="margin-top:0; color: #89b4fa;">🧪 URL Scheme & Zed Test Panel</h3>
<p style="font-size: 13px;">Test clicking different link schemes from this artifact view:</p>
<div style="display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin-top: 12px;">
<a href="zed://file/Users/matt/projects/ai-os/scripts/gen_conversation_md.py" style="background: #313244; color: #a6e3a1; padding: 8px 14px; border-radius: 6px; text-decoration: none; font-weight: bold; border: 1px solid #a6e3a1;">📝 Open gen_conversation_md.py in Zed (zed://)</a>
<a href="zed://file/Users/matt/projects/ai-os" style="background: #313244; color: #89b4fa; padding: 8px 14px; border-radius: 6px; text-decoration: none; font-weight: bold; border: 1px solid #89b4fa;">📂 Open Project Root in Zed (zed://)</a>
<a href="agyclick://open_zed?path=/Users/matt/projects/ai-os" style="background: #313244; color: #fab387; padding: 8px 14px; border-radius: 6px; text-decoration: none; font-weight: bold; border: 1px solid #fab387;">⚡ Custom Scheme (agyclick://)</a>
</div>
</div>
```

None of those open in Zed, they just open a new tab in Antigravity saying: file not found.
Any other ideas?

---

## Assistant

## Perplexity — 06:50 PM

Good news: this failure actually reveals something useful about how Antigravity's renderer works, and there's a clean two-hop workaround.

What's actually happening

Antigravity's webview isn't forwarding unrecognized schemes to the OS at all — it's treating **every** non-`http(s)` href as an internal artifact/file path and trying to resolve it inside its own sandbox. That's why `zed://`, `agyclick://`, even a correctly OS-registered scheme, all dead-end in "file not found": Antigravity never hands them off, it just fails a local lookup. Meanwhile you already confirmed `http(s)://` links *do* escape to real Chrome. So the dividing line is exactly: **only `http(s)` leaves the sandbox, nothing else does, ever.**

Separately, your Zed link syntax was also wrong — Zed's own protocol spec uses a triple-slash absolute path with no host segment: `zed:///Users/matt/projects/ai-os`, not `zed://file/Users/...`. Worth fixing regardless, but it wouldn't have helped here since Antigravity never even attempted OS resolution.
github
+1

The fix: bounce through Chrome instead of fighting it

Since `http://` is the only scheme Antigravity will actually hand off, make every clickable action point at a local HTTP endpoint, and let the redirect chain do the rest:

**Link in the artifact**: `http://127.0.0.1:PORT/open-zed?path=/Users/matt/projects/ai-os`

Antigravity forwards this navigation to real Chrome (already proven to work).

Your local server receives the GET **before** Chrome renders anything — this is the actual "click hits backend" moment you wanted. It can mutate state, regenerate `thread.md`, whatever, right here.

The server responds with an HTTP 302 to `zed:///Users/matt/projects/ai-os` (correct triple-slash form).

Chrome, a real browser, correctly resolves custom protocols against the OS's registered handler — it'll either launch Zed directly or show a one-time "Open Zed?" confirmation.
stackoverflow
+1

This works because the *browser* does proper external-protocol resolution; Antigravity's internal webview does not. You're just using Chrome as the bridge you already have working.

Cleaning up the rough edges

**Repeat permission prompts**: Chrome remembers per-scheme choices, but you can pre-authorize it so it never asks again: `defaults write com.google.Chrome URLWhitelist -array 'zed://*'` on macOS, or the equivalent `ExternalProtocolDialog` policy.
google

**The leftover Chrome tab**: after the redirect fires, Chrome is left on a blank/error page for the unhandled scheme. For pure backend-trigger buttons (delegation mode, sub-agent model, etc.) where you don't need an app launch, have the endpoint respond with a near-empty page ("✓ done — you can close this tab") or even a zero-byte `Content-Disposition: attachment` response so Chrome treats it as an instant silent download rather than a rendered page.

**Bouncing focus back to Antigravity**: unlike your custom scheme, Antigravity's *own* deep-link scheme (`antigravity-ide://`) is genuinely registered at the OS level , so a real browser resolving it will work where your webview-internal attempt didn't. You can make your server's final response redirect there instead of (or in addition to) Zed, to snap focus back to the IDE after the action completes.

This gives you the full loop: **click → real HTTP request hits your backend → state mutates → `thread.md` regenerates → (optional) OS app launches via Chrome's proper protocol handling → focus returns to Antigravity.** The only cost is a flicker of a Chrome tab per click, which you already flagged as tolerable.

---

## User

Ok, so when I click an http link, Chrome comes to the foreground and the tab opens.
Is it possible to somehow intercept that somehow and prevent that happening?
Like, even if it DID go to chrome still, if it could just do so in the background and then close the tab (I know that much is possible), that would be sick

---

## Assistant

## Perplexity — 06:50 PM

Yes — but the trick isn't to grab the tab *after* Chrome opens. By the time macOS has activated Chrome and drawn a tab, focus is already stolen and there's no clean way to un-steal it invisibly. The real fix is to **never let Chrome be the thing that receives the click at all** for these specific loopback URLs, while still forwarding everything else to Chrome normally.

The trick: become your own (invisible) default browser

macOS lets any app register as an HTTP/HTTPS handler and be set as the *default browser* — including a headless AppleScript applet with no window or Dock icon. You put a tiny router in front of Chrome:
stackoverflow
+1

**Build a 5-line AppleScript app** in Script Editor with an `on open location` handler:
stackoverflow
+1


```
text
on open location this_URL
    if this_URL starts with "http://127.0.0.1:PORT" or this_URL starts with "http://localhost:PORT" then
        do shell script "curl -s '" & this_URL & "' > /dev/null 2>&1 &"
    else
        do shell script "open -a 'Google Chrome' '" & this_URL & "'"
    end if
end open location
```


**Export it as an Application**, then edit its `Info.plist` to add `CFBundleURLTypes` for the `http`/`https` schemes, and set `LSUIElement = true` so it never shows a Dock icon or window — it's a pure background agent.
stackoverflow
+1

**Refresh Launch Services** so macOS notices the new handler: `lsregister -f /path/to/YourApp.app`.
stackoverflow

**Set it as the default browser.** Either via System Settings, or non-interactively with the `defaultbrowser` CLI tool (`brew install defaultbrowser`, then `defaultbrowser yourappname`).
github
+1

Now every `http(s)` link clicked *anywhere on the system* — including from Antigravity — is handed to your invisible router first. If it matches your loopback trigger pattern, it fires the request via `curl` in the background and does absolutely nothing visible: no window, no Dock bounce, no Chrome activation, nothing. Everything else (normal web links) gets forwarded to real Chrome exactly as before, so your everyday browsing is untouched.

Why this beats "close it after it opens"

A Chrome extension listening for `tabs.onCreated` can close the matching tab a few hundred milliseconds after it appears, but macOS has *already* activated/foregrounded Chrome as part of the "open externally" call before your extension code even runs — you'd still get a visible flash and focus steal, just a very brief one. The AppleScript-router approach intercepts one layer earlier, at the OS's URL-dispatch step, so Chrome is never launched or focused for those clicks at all.

Practical notes

Test the router thoroughly before relying on it — a bug in the forwarding branch means *all* your web links silently fail, so keep the fallback branch dead simple.

Reverting is one command: `defaultbrowser chrome`.

`curl -s ... &` backgrounds and detaches immediately so the AppleScript handler returns instantly and never shows a spinner or "busy" state for the invisible app.

If you want confirmation of success without any UI, have your local server write to a log file or update the `thread.md` artifact directly — that's already your working feedback channel.

This is a bit more setup than the link-based hacks, but it's the only approach that fully avoids Chrome ever coming to the foreground, since the interception happens before the browser is even chosen.

---
