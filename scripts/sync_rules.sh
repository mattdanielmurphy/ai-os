#!/bin/bash
# Sync system rules file to the active project repository

set -euo pipefail

SOURCE_FILE="$HOME/.gemini/GEMINI.md"
TARGET_DIR=".gemini"
TARGET_FILE="$TARGET_DIR/GEMINI.md"

# Safety check: ensure source file exists
if [ ! -f "$SOURCE_FILE" ]; then
    echo "❌ Error: Source file not found at $SOURCE_FILE" >&2
    exit 1
fi

# Ensure target directory exists in workspace
mkdir -p "$TARGET_DIR"

# Run rsync to sync files deterministically
rsync -av "$SOURCE_FILE" "$TARGET_FILE"

echo "✅ Rules synced successfully from ~/.gemini/GEMINI.md to .gemini/GEMINI.md"
