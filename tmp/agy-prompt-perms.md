You are a macOS troubleshooting agent. Investigate and fix this permissions issue:

Context: User migrated from legacy account `matthewmurphy` to new account `matt` on macOS 15.7.8. Since the migration, several permissions issues have cropped up.

Current bug: An app (unclear which one — possibly a utility like AppCleaner, CleanMyMac, or similar) tries to copy apps into /Applications/ and fails with:
> "AlDente" couldn't be copied because you don't have permission to access "Applications".

Facts I already gathered (do NOT re-gather these via terminal):
- /Applications/ is owned by root:admin with permissions drwxrwxr-x (775)
- matt IS a member of the admin group (dseditgroup -o checkmember -m matt admin -> yes)
- matthewmurphy is ALSO a member of admin
- There are NO extended ACL entries on /Applications/ (no + in ls -le)
- The only extended attributes are com.apple.appstore.* on some app bundles (standard)
- Some files inside /Applications/ are still owned by matthewmurphy

Things to investigate (you MUST actually run commands — do not just describe what to do):
1. Check console log for sandboxd / TCC denial messages related to copying into /Applications/
2. Check the TCC database: sqlite3 ~/Library/Application Support/com.apple.TCC/TCC.db for entries related to Full Disk Access, System Policy, or any app that copies/moves files
3. Check SIP status (csrutil status)
4. Check if there is a ~matthewmurphy home directory still present and if any tool/launchd/plist path references point there
5. Check if the app is sandboxed and missing the temporary-exception entitlement
6. Check fs_usage briefly or log stream for specific EPERM/EACCES denials
7. Try to identify the specific app that is doing the copying (check Applications for utility apps like AppCleaner, CleanMyMac, DropDMG, Lacona, any "installer" type apps)
8. Check ~/Library/Preferences/ and ~/Library/Application\ Support/ for paths still referencing matthewmurphy
9. Fix anything you find: grant TCC permission, update plist paths, chown files to matt, etc.

DO NOT read any source files — this is pure CLI/investigation work. Run commands, interpret output, and fix what you find. Output a clear summary of what you found and what you did.

Important: use mv not rm when moving files. Stick to terminal-only work.