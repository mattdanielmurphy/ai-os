#!/usr/bin/env bash
# scripts/memory_diff.sh
# Layer 2: Extract the exact code diff for a specific commit.

if [ -z "$1" ]; then
  echo "Usage: $0 <commit-hash>"
  exit 1
fi

commit_hash="$1"

# Validate that the commit hash exists and is a valid commit
if ! git cat-file -e "${commit_hash}^{commit}" 2>/dev/null; then
  echo "Error: '${commit_hash}' is not a valid commit hash in this repository."
  exit 1
fi

# Execute git show to get commit message and diffs
git show "$commit_hash"
