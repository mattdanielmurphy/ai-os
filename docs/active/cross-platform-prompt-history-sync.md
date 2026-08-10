# Cross-Platform Prompt & History Synchronization

## Status: Planned / Active Architectural Task

## Goal
Globally track user prompts and active issues across all projects and agent platforms (Antigravity.app, Hermes WebUI, TUI, etc.).

## Key Features
- **Cross-Project Prompt Indexing**: Detect when a user references a bug, feature, or design discussed in another project or past thread.
- **Context Pulling**: Automatically query past transcript logs (Hermes SQLite DB, Antigravity brain logs) and surface relevant past solutions.
- **Platform Agnostic**: Works regardless of whether the initial discussion took place in Hermes, Antigravity, or Zed/VSCode.
