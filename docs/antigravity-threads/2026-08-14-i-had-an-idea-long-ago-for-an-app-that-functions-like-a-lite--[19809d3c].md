---
title: "I had an idea long ago for an app that functions like a lite screenpipe. The..."
date: "2026-08-14"
conversation_id: "19809d3c-feb1-4d75-9f9e-d7fdec7d8fd5"
source: "antigravity"
---

# I had an idea long ago for an app that functions like a lite screenpipe. The...

## User

I had an idea long ago for an app that functions like a lite screenpipe. The idea is simply: I sometimes type out something, sometimes for a long amount of time and with a lot of careful thought, only to LOSE IT ALL because the app fucked it up.
Recently, this has happened specifically when typing out AI prompts.
Sometimes it's because the app I'm in fucked it up, sometimes it's something to do with having to type in a shitty TUI.
It's totally unpredictable, and when it does happen, every time, even if it's a short prompt, it's devestating.
So, as much as there's probably real benefit in having a legit screen recorder like screenpipe, that's more than I want to build right now.
I DO actually eventually want to, but make it so it's extremely lightweight, basically only storing super compressed versions of what was on screen.
But for now, let's make a really narrow-scoped version:
all I want is to see a log of everything I typed. We only have to keep like the last day really for 99% of useful cases.
In fact, it's mostly going to be: fuck, that thing swallowed my prompt or text, I need it back! open the app, recall basically the last thing typed, done.
So, it's kind of like a keylogger really, but ideally it doesn't record passwords and things typed in sensitive fields, and instead of seeing every character typed, it figures out what the text should look like by parsing the input; for example if the input log is like (chronologically)
```
a
b
c
c
Delete
d
```
Then obviously it would show me the string: `abcd` and not `abccd` or something.

And ideally when the input is being recorded the app knows which app and which window it came from; using that and I guess automatic grouping by time, we can separate the text into discrete chunks, like: this was typed into Claude Code at this time; this was typed into Chrome right after that, but it's separate because it's another app, that kind of thing.

To be clear; this is for personal use only. It COULD be spyware, but I'm not interested in spyware, I'm interested in simply never forgetting something I've typed.

---

## Assistant

## Perplexity — 02:28 PM

Yes—this is a useful, tightly scoped product: a **local, rolling “typed-text recovery buffer”**, not a screen recorder. The right V1 is a macOS menu-bar app that reconstructs editable text locally, groups it by focused app/window and time, and lets you copy the last recovered chunk in seconds.

Core product

The recovery flow should be deliberately boring: press a hotkey, see the most recent typing sessions, select the likely one, and copy its final reconstructed text. Keep a rolling 24-hour local history, with a configurable cap such as 5–50 MB, then delete old sessions automatically.

A session might read: **“Claude Code — Terminal — 9:41 PM — 6m 12s — 1,847 chars”**, followed by the final text and a short event history only when reconstruction is uncertain. This fits your local-first preference and can remain a single lightweight macOS artifact rather than becoming a Screenpipe-sized capture pipeline.

Capture model

Use a global `CGEventTap` in listen-only mode to receive keyboard events; macOS treats this as input monitoring, so the app must clearly request and explain the **Input Monitoring** permission. Quartz Event Services is Apple’s low-level facility for observing and altering input-event streams, and `CGEvent` can expose the Unicode string attached to a keyboard event—far better than maintaining a hardcoded keyboard-layout map.
developer.apple
+2

At each meaningful event, also record a small context snapshot:

Timestamp

Active app bundle ID and display name

Window title, when available

Focused accessibility element role/title, when available

Input-source / keyboard-layout identifier

Privacy classification: allowed, sensitive, or unknown

A session ID rather than raw per-key persistence

Use the Accessibility API only for context: the system-wide accessibility element exposes the focused UI element through `kAXFocusedUIElementAttribute`.
developer.apple
+1

Reconstruction engine

Do **not** store the event stream as the primary user-facing representation. Maintain an in-memory editable buffer per session:


```
text
buffer: "abcc"
cursor: 4
event: Delete
buffer: "abc"
cursor: 3
event: d
buffer: "abcd"
cursor: 4
```


Your engine needs more than insertion plus Delete:

Printable Unicode text: insert at cursor

Backspace / Forward Delete: remove before / at cursor

Left / Right, Home / End: move cursor

Shift + arrows: maintain a selection range

Typing or paste with a selection: replace selection

Command + A then typing: replace whole buffer

Return / Tab: choose whether to append a newline/tab or finalize the session based on app type

Command + V: record **“paste occurred”**, but avoid trying to silently recover clipboard contents in V1

Dead keys, IMEs, emoji pickers, dictation, and app-level autocomplete: mark the session as potentially incomplete rather than inventing text

That gives you correct recovery for the common disaster case—long prose or a prompt disappearing—while being honest about the cases a raw keyboard stream cannot faithfully reproduce.

Session boundaries

Start a new chunk when any of these occur:

Foreground app changes

Window ID/title changes

Focused input element changes substantially

Idle time exceeds roughly 20–45 seconds

A terminal command is submitted, if detectable

The user explicitly presses a “seal this chunk” hotkey

Avoid splitting merely because someone clicks within the same editor. Instead, track a stable identity like:


```
text
(bundleID, pid, windowID/title, AX role, AX identifier/description)
```


Then use time as a secondary heuristic. For terminal/TUI work, context will often only resolve to **Terminal/iTerm/Alacritty + window title**, which is still useful; the event reconstruction is what makes this project work where app-specific text APIs do not.

Privacy boundary

This is the make-or-break part: **you cannot promise “never record passwords” from keystrokes alone.** A secure native field can be identified in some cases—Apple’s `NSSecureTextField` exists specifically for password entry and masks characters—but third-party apps, browser content, custom UI frameworks, and TUIs will not expose a consistent reliable signal.
developer.apple

So V1 should be **fail closed**:

Focus state	Action
Known secure field / password-manager app	Record nothing; show a redacted gap
Known sensitive app or configurable blocked bundle ID	Record nothing
Accessibility metadata clearly indicates password/secure entry	Record nothing
Unknown editable context	Either pause by default, or capture only if the user enables “capture unknown fields”
Terminal	Capture only through an explicit opt-in, with a fast pause hotkey
Browser	Default to conservative capture; block known login/password contexts where detectable

Make the privacy state visible in the menu bar—e.g. **Recording**, **Paused**, **Sensitive field skipped**, **Unknown context skipped**—so there is never hidden behavior. Store data encrypted at rest, keep the database in an app-private local directory, provide a one-click **delete last 5 minutes** command, and never add sync, network access, analytics, or a background uploader.

Recommended stack

For this, use **native Swift**, not Tauri. The app is fundamentally a macOS event/permission/accessibility utility; Swift gives you direct access to CoreGraphics, ApplicationServices, SQLite, launch-at-login, a menu-bar UI, and code signing without a JS bridge.

I would structure it as:


```
text
TypedRecall.app
  CaptureService        CGEventTap lifecycle and permission state
  ContextService        NSWorkspace + Accessibility focus/window metadata
  ReconstructionEngine  Cursor, selection, edits, uncertainty markers
  Sessionizer           App/window/focus/idle-time grouping
  PrivacyPolicy         Allow/block/sensitive/unknown decisions
  Store                 SQLite + retention + encryption
  MenuBarUI             Recent chunks, search, copy, pause, delete
  HotkeyService         Reveal last chunk / pause / seal session
```


An event tap can appear installed yet fail to receive events if permission or runtime state is wrong, so make capture health explicit and continuously validate that the tap remains enabled.
danielraffel

Minimal V1

Build only this first:

Menu-bar-only Swift app.

Input Monitoring permission and a listen-only event tap.

Track foreground app, window title, and idle timeout.

Reconstruct ordinary insertion, backspace, delete, arrows, selection, and return.

Save rolling sessions to local SQLite.

Present the newest chunk with one hotkey: **copy most recent recovered text**.

Global pause hotkey plus app blocklist.

Hard-block obvious password managers and known secure fields.

Skip screen capture, OCR, embeddings, semantic search, cloud sync, cross-device support, and “restore text into the previous app.” Those are all future layers; the V1 only needs to answer: **“what did I just type, and can I copy it now?”**

V2 direction

Once V1 proves useful, the next strong addition is not screen recording—it is a **reliability score** per session. A chunk typed as normal Unicode with known cursor operations could show “high confidence,” while a chunk involving an IME, paste, terminal full-screen UI, or unknown focus metadata could show “partial recovery.”

Later, your extremely compressed Screenpipe-like feature can become a separate opt-in evidence layer: occasional low-resolution visual state or UI snapshots, retained briefly and linked to a typed session. Keep that entirely separate from the text-recovery core so the simple, privacy-conscious utility stays useful even if you never build the recorder.

---

## User

ok give me a prompt to have gemini build a first go at this. Be careful wording it though; I gave it the same prompt I gave you (minus the last sentence saying "to be clear this is for personal use only") and I got a security refusal, saying it won't build a keylogger.
Maybe just literally don't include the term keylogger lol.
I GET why it reacted like that, but this honestly is just for personal use.

---

## Assistant

## Perplexity — 02:28 PM

Frame it as a **local typed-text recovery utility** with strict privacy boundaries, rather than a background-monitoring tool. Gemini’s published guidance emphasizes responsible use and can apply automated/manual abuse review to prompts, so being concrete about local-only storage, consent, visible status, and hard exclusions is better than trying to obscure the functionality.
google
+1

Paste this as the initial build prompt:


```
text
Build a first working macOS prototype named “Typed Recall.”

## Product purpose

Typed Recall is a personal, local-first recovery utility for text that I have typed into my own Mac but which was lost because an app, browser page, AI chat, terminal UI, or other program unexpectedly cleared or failed to submit it.

The only core user flow for this first version is:

1. I type text in another application.
2. That application loses or swallows the text.
3. I open Typed Recall or press a hotkey.
4. I see the most recent reconstructed text sessions.
5. I copy the lost text back to my clipboard.

This is not a screen recorder, remote monitoring product, cloud service, sync service, employee-management tool, or shared-data tool. It must have no networking code, analytics, telemetry, uploading, account system, remote API, or background data transmission.

## Mandatory privacy and safety requirements

Treat these as non-negotiable product requirements:

- The app is for the signed-in Mac user only.
- All recovered text remains local on disk.
- Do not implement networking, remote access, cloud sync, telemetry, analytics, update checking, or any outbound HTTP requests.
- Do not implement stealth behavior. The app must be a normal visible menu-bar app with a clear recording state.
- The menu bar must visibly show one of: Recording, Paused, Sensitive field skipped, Permission needed, or Error.
- Include a prominent global pause/resume hotkey.
- Include “Delete recent history” and “Delete all history” actions.
- Keep only a rolling 24-hour history by default, with automatic deletion of older records.
- Do not capture or persist text while Typed Recall itself is focused.
- Do not capture text from known password-manager applications.
- If the current focused UI element is explicitly identified by macOS Accessibility APIs as a secure/password field, persist only a redacted skipped-event marker, never the entered characters.
- Include a configurable app blocklist; blocked apps must produce no captured text.
- Use conservative behavior whenever field sensitivity cannot be determined. Make this policy explicit and easy to change in one place.
- Do not claim that password detection is perfect. Present it as best-effort protection with a conservative default.
- Do not implement hidden launch, persistence tricks, privilege escalation, sandbox escape, process injection, browser extension injection, interception of other apps’ network traffic, or data exfiltration.

## Technical target

Build a native macOS app in Swift using SwiftUI and AppKit where necessary.

Prefer:
- Swift
- SwiftUI for the UI
- AppKit for menu-bar integration and global shortcuts where needed
- CoreGraphics / Quartz event APIs for observing keyboard input
- ApplicationServices Accessibility APIs for foreground/focused-element context
- SQLite or a simple local database for the rolling history

Do not use Electron, Tauri, web views, or a server process for this prototype.

Target Apple Silicon macOS first. Keep the architecture clean enough to support Intel later, but do not spend time on packaging/distribution yet.

## Explicit permission model

Implement a first-launch onboarding screen that explains why the app needs permissions in plain language.

The app may need:
- Input Monitoring, to observe keyboard events for the currently signed-in user
- Accessibility, to identify the active application, focused UI element, and whether a field reports itself as secure

Never attempt to bypass, suppress, or automate permission approval. Detect missing permissions and show the exact next action the user must take in System Settings.

## Capture and reconstruction behavior

The app should reconstruct editable text sessions instead of displaying a raw chronological list of individual key events.

Example:

Input events:
a
b
c
c
Delete
d

Recovered text:
abcd

Maintain a text buffer with:
- Text contents
- Cursor position
- Optional selected range
- Timestamp of latest edit
- Active app metadata
- Window metadata when available
- Focused-element metadata when available
- Confidence / uncertainty flags

Support this minimal editing behavior:
- Printable Unicode text insertion
- Backspace
- Forward delete
- Left and right arrow cursor movement
- Home and End where identifiable
- Shift + arrow selection movement if practical
- Replacing a selection when new normal text is typed
- Return as newline
- Tab as tab
- Command + A followed by typed text should replace the full buffer when practical
- Mark paste as an uncertainty event in V1 rather than reading or storing clipboard contents
- Mark unsupported or ambiguous input methods as uncertain instead of guessing

Do not attempt to interpret passwords, clipboard contents, dictation, IME composition, autocomplete, app-generated text, or text changed by another program. Preserve an uncertainty flag when those cases may affect recovery quality.

## Session grouping

Group typing into useful recoverable sessions.

A new session should begin when:
- The foreground application changes
- The window changes materially
- The focused element changes materially
- The user has been idle for 30 seconds
- The user manually seals the current session with a hotkey

A session should include:
- App display name
- Bundle identifier
- Window title if available
- Start and end timestamps
- Reconstructed final text
- Character count
- Confidence status
- Privacy state
- Whether it is currently active or sealed

Use a reasonable session identity based on app bundle ID, process ID, window title or ID where available, and focused-element metadata.

## Required UI

Create a polished but compact menu-bar application.

Menu bar:
- Current status
- Pause/resume capture
- Reveal recent sessions
- Copy most recent recovered session
- Delete last 5 minutes
- Delete all history
- Open settings
- Quit

Main window:
- List recent sessions, newest first
- Each row shows app name, window title when available, time, duration, character count, and confidence state
- Select a session to show its reconstructed text in a readable, selectable text view
- Copy button
- Delete session button
- Search across retained session text
- Clearly label redacted/skipped sessions without exposing content

Settings:
- Retention duration, default 24 hours
- Maximum storage amount
- Capture enabled/disabled
- Conservative privacy mode enabled by default
- App blocklist editor
- Hotkey configuration
- Clear explanation of known limitations

## Architecture

Create these components with focused responsibilities:

- AppState: app-wide status and lifecycle
- PermissionManager: Input Monitoring and Accessibility state
- CaptureService: keyboard event observation lifecycle only
- ContextService: active app, window, and focused UI-element snapshots
- PrivacyPolicy: decides capture, skip, or redact based on context
- TextReconstructionEngine: buffer/cursor/selection editing model
- SessionManager: session creation, grouping, sealing, and idle timeout
- SessionStore: local persistence, retention cleanup, deletion
- HotkeyManager: pause/resume, show latest, seal session
- MenuBarController: status item and menu actions
- MainWindow UI: session list, detail, copy, search
- Settings UI

Keep CoreGraphics / Accessibility calls isolated behind protocols so the reconstruction engine can be unit-tested without OS permissions.

## Quality bar

Before writing code, inspect the existing repository and summarize:
1. Current stack and app entry point
2. Existing files that should be reused
3. Proposed files to create or modify
4. Risks or macOS API constraints
5. A short implementation plan

Then implement the prototype in small, buildable steps.

After each meaningful step:
- Build the project
- Fix compiler errors
- Run applicable tests
- Report what changed and what remains intentionally unsupported

Add unit tests for the text reconstruction engine, including:
- Simple insertion
- Backspace
- Forward delete
- Cursor movement and insertion in the middle
- Replace selected text
- Newlines and tabs
- Session boundary after idle timeout
- Privacy policy blocks known blocked apps and secure fields
- Retention cleanup

Do not overbuild. The goal is a safe, local, usable first prototype that can recover ordinary lost prose and AI prompts, not a universal text-capture system.
```

Small adjustment

If Gemini still objects to implementing the capture layer, split the project into two prompts: first have it build **everything except `CaptureService`**, with a mock event source feeding the reconstruction engine; then ask specifically for the macOS permission/UI integration. That keeps the project buildable and lets you validate the important part—the session model, recovery UI, retention, and privacy controls—before dealing with OS-level input APIs.

---
