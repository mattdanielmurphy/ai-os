#!/bin/bash
# Find the first file in .devtool/features/ containing 'status: "in-progress"'
FEATURES_DIR=".devtool/features"

if [ ! -d "$FEATURES_DIR" ]; then
  echo "Error: $FEATURES_DIR directory does not exist." >&2
  exit 1
fi

for file in "$FEATURES_DIR"/*.md; do
  if [ -f "$file" ]; then
    if grep -q 'status: "in-progress"' "$file"; then
      echo "=== PATH: $file ==="
      cat "$file"
      exit 0
    fi
  fi
done

echo "Error: No active task containing 'status: \"in-progress\"' found." >&2
exit 1
