# Handoff chain links (context-alert 0.4.2)

## 00:30 Both links fixed

Matt asked (via the coordinator): every thread in a handoff chain links back and forward (A↔B↔C): a link at the top of the new thread, a link at the bottom of the old one, still working when the old thread is resolved.

---

### Both links were missing

Checked the last real handoff: [Mixer on built-in trackpad](#cmsg_01CUPXyY9oUwKVDFREVDpYDr6dtJeqWXZRmiWsqJMsC9hB) → [Smooth mixer fader motion](#cmsg_01CUPXyY9oUwKVDFREVDpYDrBzsyKb2XkAhavByAdGw1cD) (22:45).

- Forward link: the coordinator did send `context-alert handed-off: <new id>` to the old thread, but Remote Control delivers it as a task notification wrapped in `<project_claude_message …>`. The mod only matched a message starting with `<relay from="coordinator"`, so it never fired; the old thread's model got the note and posted nothing.
- Back link: the coordinator was asked (in free text) to make the new thread's ack "Continued from …". It didn't; the new thread opened with no link.

---

### Forward link fix

`isCoordinatorRelay` now accepts the `<project_claude_message>` wrapper. The old thread's mod posts "➡️ Handed off to [the new thread]" without waking its model. Unit test uses the exact text seen in the real transcript.

---

### Back link now posted by the mod

No longer relies on the coordinator. `cold_handoff.py write --thread <old cmsg id>` puts `<!-- context-alert parent-thread: … -->` at the top of the handoff file. The new thread's brief always names that file; the new thread's mod sees the path in its first coordinator relay, reads the marker, and posts "⬅️ Continued from [the old thread]" as the thread's first line (once per session). The coordinator brief now only asks it to keep the path word for word.

Rejected: having the new thread message the old session directly (same delivery path, no gain) and polling threads from the old one (costly).

---

### Resolved threads

message_thread reopens a resolved thread. After posting the forward link, the old thread's mod calls `set_thread_resolved` so it ends resolved again. Links into a resolved thread still open it.

---

### Chains

Each hop links its neighbour both ways, so A↔B↔C works hop by hop. Untested live: a real handoff with the new version (needs a thread to go cold). The mixer pair from 22:45 stays unlinked (only those threads' own sessions can post there).

---

### How to undo

Revert the commit "context-alert 0.4.2", then `claude plugin marketplace update ai-os-mods` and `claude plugin update context-alert@ai-os-mods` with the app's bundled binary, then restart the app.
