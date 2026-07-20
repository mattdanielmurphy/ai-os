## Goal
Enable Cmd-click on filepaths and URLs within the terminal instances (Engine and Mini).

## Changes Made
- Modified `src/main.ts` to implement a `LocalPathLinkProvider` adhering to xterm's `ILinkProvider` interface.
- Added a regex that matches absolute `/`, relative `./` or `../`, `~/`, and `file://` prefixed paths.
- Registered the new provider for both `term` and `miniTerm` using `term.registerLinkProvider()`.
- Updated the existing `handleLink` function to automatically prepend `file://` to absolute paths if they lack a protocol (like `http://` or `https://`), ensuring Tauri's `open()` handles them correctly.

## What Worked
- Web URLs are still captured by `WebLinksAddon`.
- Local filepaths are now captured by `LocalPathLinkProvider` and successfully sent to the system's `open` handler on Cmd-click.

## What Didn't Work / Known Issues
- Very short directory names or single words not forming a path with a slash (e.g. `usr` vs `usr/bin`) are not linkified to prevent false positives with generic terminal output.

## Architecture Notes
- The xterm instance handles links through addons (`WebLinksAddon`) and native providers (`registerLinkProvider`).
- Passing paths without a protocol to Tauri's `open` might not always work as a "file", so prefixing `file://` to absolute paths inside the `handleLink` callback ensures stability.
