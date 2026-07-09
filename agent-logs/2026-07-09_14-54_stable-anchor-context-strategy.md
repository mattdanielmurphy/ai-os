## Goal
Implement the **Stable Anchor + Volatile Append** strategy for workspace/codebase context orchestration by creating a lightweight signature-only repository map generator and integrating it into the `ai-os` boot process.

## User Feedback & Decisions
- Dynamically build and maintain the stable repo map during project/CLI startup rather than continuously running file watchers.
- Leverage AST (Python) and lightweight regex/line-based signature scanning (JS/TS, Rust, Go) to guarantee dependency-free parsing when tree-sitter is missing, keeping the output under 10k-15k tokens.

## Changes Made
- Created [scripts/generate_repo_map.py](file:///Users/matt/projects/ai-os/scripts/generate_repo_map.py) using `SourceFileLoader` to consume `ingest_codebase` routines for Python, and custom signature extraction filters for TS/JS, Rust, and Go files.
- Modified [bin/ai-os](file:///Users/matt/projects/ai-os/bin/ai-os) to automatically generate/update `.devtool/repo_map.txt` on application launch.

## What Worked
- Rebuilding the map compressed the workspace outline from 418KB down to a highly dense 42KB (~10k tokens) by stripping function/method bodies.
- Running the `ai-os` wrapper script successfully updates the map on startup without errors.

## What Didn't Work / Known Issues
- Importing `ingest_codebase` directly failed due to the lack of file extension. Solved using `SourceFileLoader` from `importlib.machinery`.

## Architecture Notes
- The generated `.devtool/repo_map.txt` serves as the "Stable Anchor" context. Future prompts can prepend this map before volatile files/tasks, maximizing LLM cache efficiency.
