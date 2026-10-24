#!/bin/sh
# Tweaks panel "Apply" for the explainer reels (run from the ai-os root by ~/.hammerspoon/tweaks_apps.json).
# Rebuilds every reel whose reel.json names a `page` (re-recording the voice if a voice.* knob changed),
# copies it over that page in ~/projects/pages, deploys, and refreshes its mattmurphy.ca copy if it has one.
set -e
cd "$(dirname "$0")"
for json in reels/*/reel.json; do
  page=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('page',''))" "$json")
  [ -n "$page" ] || continue
  dir=$(dirname "$json")
  python3 build.py "$dir" | tail -1
  cp "$dir/reel.html" "$HOME/projects/pages/site/$page/index.html"
  slug=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('website',''))" "$HOME/projects/pages/site/$page/page.json")
  [ -n "$slug" ] && pages publish "$page" "$slug"
done
pages deploy
