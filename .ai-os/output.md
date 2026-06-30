# Thread History Context Bug Fixed

I have successfully resolved the issue where continuing threads in `agy` would either lose context on subsequent prompts or send heavily truncated/nested histories that missed the most recent and important user request.

## Core Issues Identified & Resolved

1. **Context Cleared on Subsequent Prompts:** Previously, the frontend loaded the compactified thread context *once* when clicking a thread in the sidebar, set `activeThreadContext`, and then cleared it to `null` immediately after sending the first prompt. As a result, sending any subsequent prompts in the same thread would clear the session and attach zero historical context.
   * **Solution:** Added a dynamic lookup pattern. The frontend now stores a map of active thread log paths (`threadFilepaths`) and reads the latest transcript file directly from the filesystem *right before sending each prompt*, ensuring the context is always fully up-to-date.

2. **Truncation of the Most Recent Prompts:** When a thread was resumed, the previous prompt was stored as a combined message containing the historical context at the beginning and the actual user request at the bottom. Since the parser (`getCompactifiedContext`) truncated step prompts to 300 characters, it ended up only preserving the old history prefix and completely cutting off the actual user request.
   * **Solution:** Updated `getCompactifiedContext` to search for the last occurrence of the `User request:` marker. If present, it extracts the actual prompt from the end of the combined text, ensuring it is never cut off by truncation.

3. **Context Window Safety (Turns Cap):** We now slice the parsed conversation history to only include the last 6 steps (last 3 turns), ensuring the most recent messages (the last user prompt and assistant reply) are always sent as context, while preventing context window blowouts.

4. **New Thread Auto-Association:** Updated the backend Rust command `patch_thread_log_with_output` to return the resolved thread ID. The frontend now automatically captures this ID when a new conversation starts, ensuring the sidebar highlights the active thread and continues associating subsequent messages properly.
