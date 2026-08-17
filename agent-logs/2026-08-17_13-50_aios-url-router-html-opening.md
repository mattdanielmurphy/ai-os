# AIOSURLRouter HTML Document Opening Fix

## Objective
Fix macOS Finder error when opening `.html` files where `AIOSURLRouter` was registered as the default handler for HTML documents but failed with "AIOSURLRouter cannot open files in the 'HTML Document' format."

## Root Cause
`AIOSURLRouter.app/Contents/Info.plist` declared `CFBundleDocumentTypes` for `public.html` (required for system browser registration), but `RouterApp.swift` only implemented `handleGetURL` for `kAEGetURL` network schemes (`http://`, `https://`). When Finder opens local `.html` files, macOS invokes `NSApplicationDelegate` document handlers (`application(_:openFiles:)`, `application(_:openFile:)`, `application(_:open:)`), which were absent. AppKit consequently rejected the open event.

## Solution
1. Implemented `application(_:openFiles:)`, `application(_:openFile:)`, and `application(_:open:)` in `AppDelegate` in `tools/url-router/RouterApp.swift`.
2. Added `openInRealBrowser(urls:)` helper to dispatch local document URLs to Google Chrome (or system browser) and terminate cleanly.
3. Updated `tools/url-router/build_swift_app.sh` with `CFBundleTypeExtensions` (`html`, `htm`, `xhtml`, `shtml`) and `LSHandlerRank` in `Info.plist`.
4. Recompiled and re-registered `/Applications/AIOSURLRouter.app` with `lsregister`.