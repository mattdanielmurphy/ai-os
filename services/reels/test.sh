#!/bin/sh
# Muted headless test of a built reel, detached with a hard 2-minute limit: test.sh REEL_DIR [seconds]
# Prints the mix each second: music should sit near music.level and dip by duck.depth while she talks.
here=$(cd "$(dirname "$0")" && pwd); reel=$(cd "$1" && pwd)/reel.html; log="$here/tmp/test.log"; mkdir -p "$here/tmp"
pw=$(ls -d "$here/node_modules/playwright-core" ~/projects/*/node_modules/playwright-core 2>/dev/null | head -1)
if [ -z "$pw" ]; then  # Mac: bun. Cloud: npm (bun can't fetch through the cloud proxy)
  if [ "$CLAUDE_CODE_REMOTE" = "true" ]; then (cd "$here" && npm install --no-audit --no-fund -s); else (cd "$here" && bun install); fi
  pw="$here/node_modules/playwright-core"
fi
NODE_PATH=$(dirname "$pw") nohup perl -e 'alarm 120; exec @ARGV' node "$here/headless_test.cjs" "$reel" "${2:-20}" > "$log" 2>&1 < /dev/null &
pid=$!; while kill -0 $pid 2>/dev/null; do sleep 1; done; cat "$log"
