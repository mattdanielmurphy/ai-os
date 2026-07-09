## Goal
Fix a Rust panic where byte index slicing on non-ASCII characters inside `clean_prompt` caused a thread log parsing failure and backend crash.

## Changes Made
- Modified [src-tauri/src/main.rs](file:///Users/matthewmurphy/projects/ai-os/src-tauri/src/main.rs):
  - Replaced byte-level indexing (`&clean_prompt[..40]` and `&clean_prompt[..120]`) with character-based slicing using `.chars().take(40).collect::<String>()` and `.chars().take(120).collect::<String>()`. This ensures safe truncation at Unicode scalar boundaries, preventing panics on multibyte characters like en-dashes (`–`).

## What Worked
- Implementing Unicode-safe character slicing in Rust.
- Verifying the Rust compilation via `cargo check` to ensure correctness.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Rust's `&str[..n]` indexes by byte offset rather than character count. Slicing user-provided input strings directly using byte offsets can split multibyte UTF-8 codepoints, leading to a program panic. Always use `.chars().take(count).collect::<String>()` or a similar character boundary validator for safety.
