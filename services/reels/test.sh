#!/bin/sh
# Muted headless test of a built reel, detached with a hard 2-minute limit: test.sh REEL_DIR [seconds]
# Prints the mix each second: music should sit near music.level and dip by duck.depth while she talks.
here=$(cd "$(dirname "$0")" && pwd); reel=$(cd "$1" && pwd)/reel.html; log="$here/tmp/test.log"; mkdir -p "$here/tmp"
pw=$(ls -d ~/projects/*/node_modules/playwright-core 2>/dev/null | head -1)
[ -n "$pw" ] || { echo "needs playwright-core in some ~/projects/*/node_modules"; exit 1; }
NODE_PATH=$(dirname "$pw") nohup perl -e 'alarm 120; exec @ARGV' node "$here/headless_test.cjs" "$reel" "${2:-20}" > "$log" 2>&1 < /dev/null &
pid=$!; while kill -0 $pid 2>/dev/null; do sleep 1; done; cat "$log"
