---
title: "Fixing Default HTML Browser"
date: "2026-08-17"
conversation_id: "abca1cf4-a8c7-4aee-b811-471d55ce3ace"
source: "antigravity"
---

# Fixing Default HTML Browser

## User

when I try to open html files in Finder, I get this error.
If I open inspector and change the default app, it changes back to this router. It may well be that this is what makes this actually work. That's cool, but I need html files to just open in my REAL browser even if it's opening in this router app first.
/_plan-with-ai-os

---

## Assistant

I have dispatched the high-reasoning planning task via AI-OS to analyze the `AIOSURLRouter` HTML document handler error and formulate the implementation plan. 

I will process the results and present the implementation plan as soon as the planner completes.

The initial query timed out, so I have initiated the recovery command (`--recover`) to fetch the completed plan from the ongoing AI-OS session.

I'll process and present the implementation plan as soon as it arrives.

I have analyzed the root cause and created the implementation plan to fix HTML file opening in `AIOSURLRouter`:

### Root Cause
`AIOSURLRouter.app` declares `CFBundleDocumentTypes` for `HTML Document` in `Info.plist` (which macOS requires for default browser registration), but `tools/url-router/RouterApp.swift` only implemented `handleGetURL` for `kAEGetURL` network schemes (`http://`, `https://`). When Finder attempts to open `.html` files, macOS invokes document delegate methods (`application(_:openFiles:)`), which were missing on `AppDelegate`, causing AppKit to reject opening the document with the error modal.

### Solution
1. Add `application(_:openFiles:)`, `application(_:openFile:)`, and `application(_:openURLs:)` in [RouterApp.swift](file:///Users/matt/projects/ai-os/tools/url-router/RouterApp.swift) to forward local HTML files directly to Google Chrome (or system browser).
2. Update [build_swift_app.sh](file:///Users/matt/projects/ai-os/tools/url-router/build_swift_app.sh) to include file extensions (`html`, `htm`, `xhtml`) in `Info.plist`, recompile `AIOSURLRouter`, and re-register with `lsregister`.

Please review the plan in [implementation_plan.md](file:///Users/matt/.gemini/antigravity/brain/abca1cf4-a8c7-4aee-b811-471d55ce3ace/implementation_plan.md) and let me know if you'd like me to proceed.

---

## Assistant

I have invoked the `file_editor` subagent to write the updated implementations to [RouterApp.swift](file:///Users/matt/projects/ai-os/tools/url-router/RouterApp.swift) and [build_swift_app.sh](file:///Users/matt/projects/ai-os/tools/url-router/build_swift_app.sh). I will verify and build the app as soon as the updates complete.

I have instructed the subagent to execute the writes to both files and will verify the changes immediately upon completion.

I have instructed the subagent to record the engineering log and update `DEVELOPMENT_JOURNAL.md`.

### Changes Completed

1. **Implemented AppKit Document Delegate Handlers**:
   - In [`RouterApp.swift`](file:///Users/matt/projects/ai-os/tools/url-router/RouterApp.swift), implemented `application(_:openFiles:)`, `application(_:openFile:)`, and `application(_:open:)` on `AppDelegate`.
   - Added `openInRealBrowser(urls:)` to forward local `.html` files and `file://` URLs directly to Google Chrome (or system browser fallback) and exit cleanly.

2. **Updated Info.plist & Rebuilt Application Bundle**:
   - In [`build_swift_app.sh`](file:///Users/matt/projects/ai-os/tools/url-router/build_swift_app.sh), updated `CFBundleDocumentTypes` with file extensions (`html`, `htm`, `xhtml`, `shtml`) and `LSHandlerRank: Alternate`.
   - Recompiled `AIOSURLRouter`, re-signed the app bundle, and re-registered `/Applications/AIOSURLRouter.app` with LaunchServices (`lsregister`).

3. **Verification**:
   - Verified that opening HTML files via `AIOSURLRouter` now routes and opens directly in Google Chrome without any error modals.

For details, see [walkthrough.md](file:///Users/matt/.gemini/antigravity/brain/abca1cf4-a8c7-4aee-b811-471d55ce3ace/walkthrough.md) and [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md).

---
