# Postflight File Link Formatter & Action Button Postprocessor

## Status: Active Design / High Priority Task

## Goal
Eliminate model overhead and token waste for complex file link formatting by delegating link enrichment to an automated postprocessor in `postflight.py` (or post-turn hook).

## Requirements & Behavior
Agents output standard `file://` markdown links. The postprocessor intercepts the final turn output and enriches all file links with interactive action triggers based on file extension.

### Link Action Matrix

1. **Markdown Files (`.md`)**:
   - **Primary Action (Click Link)**: Opens in Antigravity Artifact Viewer (`file://...`).
   - **Secondary Action 1 (Icon)**: Open in Zed (`zed://` / `ai-os open-in-zed`).
   - **Secondary Action 2 (Icon / Menu)**: Reveal in macOS Finder (`ai-os reveal`).
   - **Menu Option**: Copy absolute pathname to clipboard.

2. **All Other Files (Code, Config, Assets)**:
   - **Primary Action (Click Link)**: Opens in Zed (`zed://...`).
   - **Secondary Action 1 (Icon)**: Reveal in macOS Finder (`ai-os reveal`).
   - **Menu Option**: Open in Antigravity Artifact Viewer (`file://...`).
   - **Menu Option**: Copy absolute pathname to clipboard.

## Architecture
- **Zero Agent Overhead**: Agents do not write complex HTML button code. They write plain markdown links.
- **Hook Integration**: Executed automatically during `postflight.py` / `watch_transcripts.py` stream processing.
