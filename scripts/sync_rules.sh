#!/bin/bash
# Bidirectional Newer-Wins Sync for rules files

set -euo pipefail

GLOBAL_FILE="/Users/matt/.gemini/GEMINI.md"
LOCAL_DIR="/Users/matt/projects/ai-os/.gemini"
LOCAL_FILE="$LOCAL_DIR/GEMINI.md"

# Ensure directories exist
mkdir -p "$LOCAL_DIR"
mkdir -p "$(dirname "$GLOBAL_FILE")"

# If neither exists, we can't do anything
if [ ! -f "$GLOBAL_FILE" ] && [ ! -f "$LOCAL_FILE" ]; then
    echo "❌ Error: Neither global nor local GEMINI.md exists." >&2
    exit 1
fi

# Handle cases where only one file exists
if [ -f "$GLOBAL_FILE" ] && [ ! -f "$LOCAL_FILE" ]; then
    echo "📥 Local file missing. Copying global to local..."
    cp "$GLOBAL_FILE" "$LOCAL_FILE"
    exit 0
fi

if [ ! -f "$GLOBAL_FILE" ] && [ -f "$LOCAL_FILE" ]; then
    echo "📤 Global file missing. Copying local to global..."
    cp "$LOCAL_FILE" "$GLOBAL_FILE"
    exit 0
fi

# Both exist. Compare modification times.
GLOBAL_MOD=$(stat -f %m "$GLOBAL_FILE")
LOCAL_MOD=$(stat -f %m "$LOCAL_FILE")

if [ "$GLOBAL_MOD" -gt "$LOCAL_MOD" ]; then
    echo "📥 Global file is newer. Copying to local..."
    rsync -av "$GLOBAL_FILE" "$LOCAL_FILE"
elif [ "$LOCAL_MOD" -gt "$GLOBAL_MOD" ]; then
    echo "📤 Local file is newer. Copying to global..."
    rsync -av "$LOCAL_FILE" "$GLOBAL_FILE"
else
    echo "✅ Rules are already identical and in sync."
fi

echo ""
echo "🔄 Syncing modular config rules..."
GLOBAL_RULES_DIR="/Users/matt/.gemini/config/rules/"
LOCAL_RULES_DIR="/Users/matt/projects/ai-os/config/rules/"

mkdir -p "$GLOBAL_RULES_DIR"
mkdir -p "$LOCAL_RULES_DIR"

# Rsync with --update (-u) will skip files that are newer on the receiver
echo "📥 Syncing from global to local..."
rsync -auv "$GLOBAL_RULES_DIR" "$LOCAL_RULES_DIR"
echo "📤 Syncing from local to global..."
rsync -auv "$LOCAL_RULES_DIR" "$GLOBAL_RULES_DIR"

echo "✅ Modular rules sync complete."

