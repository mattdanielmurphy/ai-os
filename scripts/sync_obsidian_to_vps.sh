#!/usr/bin/env bash
# scripts/sync_obsidian_to_vps.sh
# Syncs Matt's local Obsidian iCloud vault to Oracle Cloud VPS mirror.

set -euo pipefail

VAULT="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/"
DEST="oracle-minecraft-server:~/obsidian/personal/"

if [ -d "$VAULT" ]; then
    rsync -az --delete \
        --exclude ".git" \
        --exclude ".obsidian/workspace*" \
        --exclude ".obsidian/cache*" \
        --exclude ".trash" \
        --exclude "*.tmp" \
        "$VAULT" "$DEST"
fi
