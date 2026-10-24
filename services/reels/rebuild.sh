#!/bin/sh
# Rebuild a reel after changing tweaks.json (cached voice, ~10 s): ./rebuild.sh 004-dad-iptv
# Prints the file to open (add ?mute). Publishing to claude.ai needs a Claude session (Artifact tool).
cd "$(dirname "$0")" && python3 build.py "reels/${1:?reel folder, e.g. 004-dad-iptv}" | tail -1
