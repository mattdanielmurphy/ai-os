#!/usr/bin/env bash
# scripts/memory_search.sh
# Layer 1: Search repository history for keywords in commit messages or diff contents.

if [ -z "$1" ]; then
  echo "Usage: $0 <keyword>"
  exit 1
fi

keyword="$1"

# Get commit hashes matching the grep (in commit messages) or -S (in diff contents)
# awk '!seen[$0]++' preserves the order of the first appearance (newest first)
hashes=$( (git log --grep="$keyword" --format="%H"; git log -S"$keyword" --format="%H") | awk '!seen[$0]++' )

if [ -z "$hashes" ]; then
  echo "No commits found matching '$keyword'."
  exit 0
fi

# Print formatted output
echo "$hashes" | while read -r hash; do
  if [ -n "$hash" ]; then
    git log -1 --format="[%h] - %s" "$hash"
  fi
done
