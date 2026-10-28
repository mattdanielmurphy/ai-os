# Handoff: context-alert—attachments + managed settings (2026-10-18, cold)

## Chain
- Old thread: 4aceae6a-1554-4bd3-8e83-1ade88ed62e6 (Expired thread cache detection). Reopen with `claude --resume 4aceae6a-1554-4bd3-8e83-1ade88ed62e6` if needed.
- Earlier handoff: `docs/handoffs/2026-10-18_expired-thread-cache-detection-cold.md`.

## Chain summary
- **Built context-alert mod:** detects cold threads (>1h old), shows "Fresh thread" band with `/fresh` command and button to start new thread with fresh context handoff.
- **Fixed held message loss:** messages in drafts now carry to new thread in paste prompt as "Read <handoff> and continue. Then: <message>".
- **Extended to attachments:** images/files now save to `tmp/held/`, paths embedded in new prompt. Requires managed settings to grant app permission.
- **Quotes always traveled** (they're plain text); only real file/image attachments were missing before.

## This thread
- Verified message carry works (mod test + code review).
- Fixed script-path bug: mod now uses full repo path to `cold_handoff.py`, not relative, since app runs cached copy of the mod.
- Implemented attachment saving: read, base64-decode via stdin, write to `tmp/held/`, include paths in new prompt.
- Installed managed-settings.json to `/Library/Application Support/ClaudeCode/` (one-time setup, grants plugin file-read scope).
- Version 0.2.2: all 6 tests pass, type-check clean. Pushed to repo.
- **Blocker:** app still has old 0.2.1 cached in memory; restart needed to load new version.

## Working on now
**Waiting on app restart.** Once Matt restarts Claude app:
1. Run `/status` to confirm "Enterprise managed settings (file)" appears.
2. Test on phone: send image + message into old thread, send `/fresh`, verify new prompt includes `tmp/held/<filename>` paths.
3. If managed settings don't activate: remove `context-alert@ai-os-mods` from `~/.claude/settings.json`, restart again.

## Keep in mind
- **App caches mods.** Repo edits don't load until app restart—this is the blocker.
- **Managed settings path is critical:** `/Library/Application Support/ClaudeCode/managed-settings.json`. Bad JSON breaks Claude Code startup entirely.
- **Phone only:** held messages exist only on phone (post-send). Mac shows band pre-send, so Fresh thread works before attaching files.
- **Fallback:** if managed settings don't activate, attachment reading degrades to "can't come along" warning with filenames listed.
- **Managed settings grant:** the file specifies which plugin scopes are enabled (file read for context-alert).

## Next steps
1. Restart Claude app (quit fully, reopen).
2. Run `/status` in any thread—confirm "Enterprise managed settings (file)" under "Setting sources".
3. Test on phone: image + message in a 1h+ old thread, send `/fresh`, check new prompt ends with `tmp/held/…` path.

## Read first
- `docs/handoffs/2026-10-18_expired-thread-cache-detection-cold.md` — context, mod purpose, phone vs Mac flows.
- `/Users/matt/.claude/dev-mods/4aceae6a-1554-4bd3-8e83-1ade88ed62e6/context-alert/hooks/register.tsx` — core logic, `readAttachments()`, managed-settings helper.
- `~/projects/ai-os/tmp/managed-settings.json` — what was installed; shows plugin scope grants.

Paste into a new thread: "Read /Users/matt/projects/ai-os/docs/handoffs/2026-10-18_expired-thread-cache-detection-cold_2.md and continue."
