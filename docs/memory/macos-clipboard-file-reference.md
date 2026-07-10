# macOS Clipboard: Copying File References

To copy a **file reference** (not the file contents) to the macOS clipboard — so that pasting inserts the actual file, not its text — use the AppKit `NSPasteboard` with `NSURL`:

```bash
FILE="/absolute/path/to/file.txt"
swift -e "
import AppKit
let pb = NSPasteboard.general
pb.clearContents()
let url = NSURL(fileURLWithPath: \"$FILE\")
pb.writeObjects([url])
" 2>/dev/null
```

This puts a `public.file-url` pasteboard type on the clipboard, which Finder and most macOS apps recognize as a file reference.

## Why not `osascript`?

The AppleScript approach (`set the clipboard to POSIX file "..." as alias`) puts an old-style `alias` record on the clipboard. Many modern apps don't recognize it when pasting, resulting in a silent no-op.

The Swift/AppKit `NSURL` approach produces the `public.file-url` type — the modern standard that works reliably in Finder, editors, and other macOS applications.

## Helper script

This project has a ready-to-use helper at `bin/copy-file-ref`:

```bash
./bin/copy-file-ref ./some/file.txt
```