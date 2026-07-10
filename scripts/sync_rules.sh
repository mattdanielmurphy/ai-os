#!/bin/bash
# Sync system rules file to the active project repository

set -euo pipefail

SOURCE_FILE="$HOME/.gemini/GEMINI.md"
TARGET_DIR=".gemini"
TARGET_FILE="$TARGET_DIR/GEMINI.md"

# Safety check: ensure source file exists and is not empty
if [ ! -f "$SOURCE_FILE" ]; then
    echo "❌ Error: Source file not found at $SOURCE_FILE" >&2
    exit 1
fi

# Safety check: if target exists and is not empty, but source is empty, print warning and exit 0
if [ -s "$TARGET_FILE" ] && [ ! -s "$SOURCE_FILE" ]; then
    echo "⚠️ Warning: Target file $TARGET_FILE exists and is not empty, but source file $SOURCE_FILE is empty. Skipping rsync." >&2
    exit 0
fi

# Ensure target directory exists in workspace
mkdir -p "$TARGET_DIR"

# Run rsync to sync files deterministically
rsync -av "$SOURCE_FILE" "$TARGET_FILE"

echo "✅ Rules synced successfully from ~/.gemini/GEMINI.md to .gemini/GEMINI.md"
